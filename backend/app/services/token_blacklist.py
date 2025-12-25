"""Token blacklist service for server-side session invalidation."""
from datetime import datetime
from typing import Optional

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import logger


# Redis key prefix
BLACKLIST_PREFIX = "token_blacklist:"
SESSION_PREFIX = "active_session:"


class TokenBlacklist:
    """
    Redis-based token blacklist for invalidating JWT tokens before expiry.

    Features:
    - Add tokens to blacklist with automatic expiry
    - Check if a token (JTI) is blacklisted
    - Track active sessions per user
    - Automatic cleanup via Redis TTL
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def add(self, jti: str, expires_in_seconds: int) -> bool:
        """
        Add a token JTI to the blacklist.

        Args:
            jti: JWT ID to blacklist
            expires_in_seconds: Seconds until the token naturally expires
                              (blacklist entry will auto-expire then)

        Returns:
            True if added successfully, False on error
        """
        if expires_in_seconds <= 0:
            return True  # Token already expired

        key = f"{BLACKLIST_PREFIX}{jti}"

        try:
            await self.redis.setex(
                key,
                expires_in_seconds,
                datetime.utcnow().isoformat()
            )
            logger.debug(f"Added token {jti[:8]}... to blacklist for {expires_in_seconds}s")
            return True
        except Exception as e:
            logger.error(f"Failed to add token to blacklist: {e}")
            return False

    async def add_with_expiry(self, jti: str, expires_at: datetime) -> bool:
        """
        Add a token JTI to blacklist until its expiry time.

        Args:
            jti: JWT ID to blacklist
            expires_at: When the token naturally expires

        Returns:
            True if added successfully, False on error
        """
        expires_in = int((expires_at - datetime.utcnow()).total_seconds())
        return await self.add(jti, expires_in)

    async def is_blacklisted(self, jti: str) -> bool:
        """
        Check if a token JTI is blacklisted.

        Args:
            jti: JWT ID to check

        Returns:
            True if blacklisted, False otherwise
        """
        key = f"{BLACKLIST_PREFIX}{jti}"

        try:
            exists = await self.redis.exists(key)
            return bool(exists)
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            # Fail closed for security - treat as blacklisted on error
            return True

    async def remove(self, jti: str) -> bool:
        """
        Remove a token from the blacklist (rarely needed).

        Args:
            jti: JWT ID to remove

        Returns:
            True if removed, False on error
        """
        key = f"{BLACKLIST_PREFIX}{jti}"

        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to remove token from blacklist: {e}")
            return False

    async def blacklist_all_user_tokens(
        self,
        user_id: str,
        token_lifetime_seconds: int = None
    ) -> int:
        """
        Blacklist all tokens for a user (emergency logout).

        Note: This requires tracking active tokens per user.
        For now, this stores a "logout all" marker that should be
        checked during token validation.

        Args:
            user_id: User ID to blacklist all tokens for
            token_lifetime_seconds: How long to keep the marker

        Returns:
            0 (marker set, actual count unknown without session tracking)
        """
        if token_lifetime_seconds is None:
            token_lifetime_seconds = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

        key = f"user_logout_all:{user_id}"

        try:
            await self.redis.setex(
                key,
                token_lifetime_seconds,
                datetime.utcnow().isoformat()
            )
            logger.info(f"Set logout-all marker for user {user_id}")
            return 0
        except Exception as e:
            logger.error(f"Failed to set logout-all marker: {e}")
            return 0

    async def is_user_logged_out_all(self, user_id: str, token_iat: datetime) -> bool:
        """
        Check if a user has a "logout all" marker newer than the token.

        Args:
            user_id: User ID to check
            token_iat: When the token was issued

        Returns:
            True if user logged out all sessions after token was issued
        """
        key = f"user_logout_all:{user_id}"

        try:
            logout_time_str = await self.redis.get(key)
            if not logout_time_str:
                return False

            logout_time = datetime.fromisoformat(logout_time_str.decode())
            return logout_time > token_iat
        except Exception as e:
            logger.error(f"Failed to check logout-all marker: {e}")
            # Fail closed for security
            return True

    # Session tracking methods

    async def register_session(
        self,
        user_id: str,
        jti: str,
        expires_in_seconds: int,
        metadata: dict = None
    ) -> bool:
        """
        Register an active session for a user.

        Args:
            user_id: User ID
            jti: JWT ID
            expires_in_seconds: Session TTL
            metadata: Optional session metadata (device, IP, etc.)

        Returns:
            True if registered successfully
        """
        key = f"{SESSION_PREFIX}{user_id}:{jti}"

        try:
            value = {
                "created_at": datetime.utcnow().isoformat(),
                **(metadata or {})
            }
            await self.redis.setex(
                key,
                expires_in_seconds,
                str(value)
            )
            return True
        except Exception as e:
            logger.error(f"Failed to register session: {e}")
            return False

    async def get_active_sessions(self, user_id: str) -> list[str]:
        """
        Get all active session JTIs for a user.

        Returns:
            List of active JWT IDs
        """
        pattern = f"{SESSION_PREFIX}{user_id}:*"

        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                # Extract JTI from key
                jti = key.decode().split(":")[-1]
                keys.append(jti)
            return keys
        except Exception as e:
            logger.error(f"Failed to get active sessions: {e}")
            return []

    async def get_session_count(self, user_id: str) -> int:
        """
        Get count of active sessions for a user.

        Returns:
            Number of active sessions
        """
        sessions = await self.get_active_sessions(user_id)
        return len(sessions)

    async def remove_session(self, user_id: str, jti: str) -> bool:
        """
        Remove a session registration (on logout).

        Args:
            user_id: User ID
            jti: JWT ID

        Returns:
            True if removed
        """
        key = f"{SESSION_PREFIX}{user_id}:{jti}"

        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to remove session: {e}")
            return False

    async def remove_all_sessions(self, user_id: str) -> int:
        """
        Remove all session registrations for a user.

        Returns:
            Number of sessions removed
        """
        pattern = f"{SESSION_PREFIX}{user_id}:*"
        count = 0

        try:
            async for key in self.redis.scan_iter(match=pattern):
                await self.redis.delete(key)
                count += 1
            return count
        except Exception as e:
            logger.error(f"Failed to remove all sessions: {e}")
            return count


# Global instance (initialized on first use)
_blacklist_instance: Optional[TokenBlacklist] = None


async def get_token_blacklist(redis_client: redis.Redis) -> TokenBlacklist:
    """Get or create the token blacklist instance."""
    global _blacklist_instance
    if _blacklist_instance is None:
        _blacklist_instance = TokenBlacklist(redis_client)
    return _blacklist_instance


def create_token_blacklist(redis_client: redis.Redis) -> TokenBlacklist:
    """Create a new token blacklist instance."""
    return TokenBlacklist(redis_client)
