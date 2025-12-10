"""Rate limiting functionality using Redis for distributed rate limiting."""

import time
from typing import Callable, Optional
from fastapi import Request, HTTPException, status
from redis.asyncio import Redis, from_url

from app.core.config import settings


class RateLimiter:
    """
    Rate limiter using Redis with sliding window algorithm.

    This implementation uses Redis sorted sets to track requests within a time window,
    providing accurate rate limiting even in distributed environments.
    """

    def __init__(self, redis_url: str):
        """
        Initialize the rate limiter.

        Args:
            redis_url: Redis connection URL
        """
        self.redis: Optional[Redis] = None
        self.redis_url = redis_url

    async def get_redis(self) -> Redis:
        """Get or create Redis connection."""
        if self.redis is None:
            self.redis = from_url(self.redis_url, decode_responses=True)
        return self.redis

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """
        Check if a request is within rate limits using sliding window.

        Args:
            key: Unique identifier for the rate limit (e.g., "login:user@example.com")
            max_requests: Maximum number of requests allowed in the window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (is_allowed, remaining_requests)

        Example:
            allowed, remaining = await limiter.check_rate_limit(
                "login:user@example.com",
                max_requests=5,
                window_seconds=60
            )
            if not allowed:
                raise HTTPException(status_code=429, detail="Too many requests")
        """
        redis = await self.get_redis()
        now = time.time()
        window_start = now - window_seconds

        # Remove old entries outside the window
        await redis.zremrangebyscore(key, 0, window_start)

        # Count current requests in window
        current_requests = await redis.zcard(key)

        if current_requests >= max_requests:
            # Rate limit exceeded
            return False, 0

        # Add current request with timestamp as score
        await redis.zadd(key, {str(now): now})

        # Set expiration on the key (cleanup)
        await redis.expire(key, window_seconds)

        remaining = max_requests - current_requests - 1
        return True, remaining

    def create_limiter_dependency(
        self,
        max_requests: int,
        window_seconds: int,
        key_func: Optional[Callable[[Request], str]] = None,
        error_message: str = "Too many requests. Please try again later.",
    ):
        """
        Create a FastAPI dependency for rate limiting.

        Args:
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
            key_func: Function to extract rate limit key from request.
                     Defaults to using client IP address.
            error_message: Custom error message for rate limit exceeded

        Returns:
            FastAPI dependency function

        Example:
            # Rate limit by IP address (default)
            limiter = RateLimiter(settings.REDIS_URL)
            login_rate_limit = limiter.create_limiter_dependency(
                max_requests=5,
                window_seconds=60
            )

            # Rate limit by custom key (e.g., email)
            def get_email_key(request: Request) -> str:
                body = await request.json()
                return f"magic-link:{body.get('email', 'unknown')}"

            magic_link_rate_limit = limiter.create_limiter_dependency(
                max_requests=3,
                window_seconds=3600,
                key_func=get_email_key
            )

            # Use in endpoint
            @router.post("/login")
            async def login(
                request: LoginRequest,
                _: None = Depends(login_rate_limit)
            ):
                ...
        """

        async def rate_limit_dependency(request: Request):
            """Rate limit dependency function."""
            # Determine the rate limit key
            if key_func:
                try:
                    key = key_func(request)
                except Exception:
                    # If custom key extraction fails, fall back to IP
                    key = f"ratelimit:{request.client.host if request.client else 'unknown'}"
            else:
                # Default: rate limit by IP address
                client_ip = request.client.host if request.client else "unknown"
                # Include the endpoint path to have separate limits per endpoint
                endpoint = request.url.path
                key = f"ratelimit:{endpoint}:{client_ip}"

            # Check rate limit
            allowed, remaining = await self.check_rate_limit(
                key=key,
                max_requests=max_requests,
                window_seconds=window_seconds,
            )

            if not allowed:
                # Add rate limit headers
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=error_message,
                    headers={
                        "X-RateLimit-Limit": str(max_requests),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time() + window_seconds)),
                        "Retry-After": str(window_seconds),
                    },
                )

            # Add rate limit info to headers (FastAPI will merge these)
            request.state.rate_limit_remaining = remaining
            request.state.rate_limit_limit = max_requests

        return rate_limit_dependency


# Global rate limiter instances
_auth_limiter: Optional[RateLimiter] = None
_api_limiter: Optional[RateLimiter] = None


def get_auth_limiter() -> RateLimiter:
    """Get or create the authentication rate limiter."""
    global _auth_limiter
    if _auth_limiter is None:
        _auth_limiter = RateLimiter(settings.REDIS_URL)
    return _auth_limiter


def get_api_limiter() -> RateLimiter:
    """Get or create the general API rate limiter."""
    global _api_limiter
    if _api_limiter is None:
        _api_limiter = RateLimiter(settings.REDIS_URL)
    return _api_limiter


# Pre-configured rate limit dependencies for common use cases

# Login: 5 requests per minute per IP (prevent brute force)
def login_rate_limit(request: Request):
    """Rate limit for login endpoint: 5 requests per minute."""
    limiter = get_auth_limiter()
    return limiter.create_limiter_dependency(
        max_requests=5,
        window_seconds=60,
        error_message="Too many login attempts. Please try again in a minute.",
    )(request)


# Registration: 10 requests per hour per IP (prevent abuse)
def register_rate_limit(request: Request):
    """Rate limit for registration endpoint: 10 requests per hour."""
    limiter = get_auth_limiter()
    return limiter.create_limiter_dependency(
        max_requests=10,
        window_seconds=3600,
        error_message="Too many registration attempts. Please try again later.",
    )(request)


# Magic link: 3 requests per hour per email (prevent spam)
def magic_link_rate_limit_by_ip(request: Request):
    """Rate limit for magic link endpoint: 3 requests per hour per IP."""
    limiter = get_auth_limiter()
    return limiter.create_limiter_dependency(
        max_requests=3,
        window_seconds=3600,
        error_message="Too many magic link requests. Please try again later.",
    )(request)


# General API: 60 requests per minute per IP
def api_rate_limit(request: Request):
    """Rate limit for general API endpoints: 60 requests per minute."""
    limiter = get_api_limiter()
    return limiter.create_limiter_dependency(
        max_requests=60,
        window_seconds=60,
        error_message="Rate limit exceeded. Please slow down your requests.",
    )(request)


# Stats endpoint: 30 requests per minute per IP
def stats_rate_limit(request: Request):
    """Rate limit for stats endpoint: 30 requests per minute."""
    limiter = get_api_limiter()
    return limiter.create_limiter_dependency(
        max_requests=30,
        window_seconds=60,
        error_message="Too many requests to stats endpoint. Please try again later.",
    )(request)
