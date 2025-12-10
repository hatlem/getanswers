"""Redis client for caching and rate limiting."""

import redis.asyncio as redis
from typing import Optional
from app.core.config import settings


class RedisClient:
    """Async Redis client wrapper for application-wide use."""

    _client: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """Get or create Redis client instance."""
        if cls._client is None:
            cls._client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
        return cls._client

    @classmethod
    async def close(cls):
        """Close Redis connection."""
        if cls._client:
            await cls._client.close()
            cls._client = None


async def get_redis() -> redis.Redis:
    """Dependency for getting Redis client."""
    return await RedisClient.get_client()
