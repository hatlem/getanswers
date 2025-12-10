from typing import Optional
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError, NotFoundError
from app.core.logging import logger
from app.models import User

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    Validates JWT token from Authorization header and returns the user.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        User object for the authenticated user

    Raises:
        AuthenticationError: If token is invalid, expired, or user not found
    """
    token = credentials.credentials

    try:
        payload = verify_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise AuthenticationError("Invalid authentication credentials")
    except ValueError as e:
        logger.warning(f"Token verification failed: {e}")
        raise AuthenticationError(str(e))

    # Query user from database
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Database error while fetching user: {e}", exc_info=True)
        raise AuthenticationError("Failed to authenticate user")

    if user is None:
        logger.warning(f"User not found for ID: {user_id}")
        raise AuthenticationError("User not found")

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional dependency to get the current authenticated user.
    Returns None if no valid authentication is provided instead of raising an error.

    Args:
        credentials: Optional HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials

    try:
        payload = verify_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            return None

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user
    except (ValueError, Exception):
        return None
