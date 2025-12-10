"""Gmail OAuth integration API endpoints.

This module provides endpoints for:
- Gmail OAuth authorization flow
- Token management and refresh
- Gmail disconnection
"""

import json
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.services import GmailService, GmailAuthError, GmailAPIError
from app.services.dependencies import get_gmail_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/gmail", tags=["Gmail OAuth"])


# Request/Response Schemas
class AuthorizationUrlResponse(BaseModel):
    """Response containing Gmail OAuth authorization URL."""
    authorization_url: str = Field(description="URL to redirect user to for Gmail authorization")
    user_id: UUID = Field(description="User ID for tracking")


class GmailCallbackRequest(BaseModel):
    """Request body for OAuth callback."""
    code: str = Field(description="Authorization code from Google OAuth")
    state: Optional[str] = Field(None, description="State parameter from OAuth flow")


class GmailConnectionStatus(BaseModel):
    """Gmail connection status response."""
    connected: bool = Field(description="Whether Gmail is connected")
    email: Optional[str] = Field(None, description="Connected Gmail address")
    connected_at: Optional[str] = Field(None, description="When the connection was established")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


@router.get("", response_model=AuthorizationUrlResponse)
async def get_gmail_authorization_url(
    redirect_uri: str = Query(..., description="OAuth redirect URI (callback URL)"),
    current_user: User = Depends(get_current_user),
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """Generate Gmail OAuth authorization URL.

    This endpoint starts the OAuth flow by generating an authorization URL
    that the client should redirect the user to for granting Gmail access.

    Args:
        redirect_uri: The callback URL where Google will redirect after authorization
        current_user: Authenticated user from JWT token
        gmail_service: Gmail service instance

    Returns:
        Authorization URL and user ID

    Example:
        GET /api/auth/gmail?redirect_uri=http://localhost:5073/gmail/callback

        Response:
        {
            "authorization_url": "https://accounts.google.com/o/oauth2/auth?...",
            "user_id": "123e4567-e89b-12d3-a456-426614174000"
        }
    """
    try:
        authorization_url = await gmail_service.get_authorization_url(
            user_id=str(current_user.id),
            redirect_uri=redirect_uri
        )

        logger.info(f"Generated Gmail authorization URL for user {current_user.id}")

        return AuthorizationUrlResponse(
            authorization_url=authorization_url,
            user_id=current_user.id
        )

    except GmailAuthError as e:
        logger.error(f"Gmail auth error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate authorization URL: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error generating auth URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/callback", response_model=GmailConnectionStatus)
async def gmail_oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter containing user_id"),
    redirect_uri: str = Query(..., description="OAuth redirect URI (must match authorization request)"),
    db: AsyncSession = Depends(get_db),
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """Handle Gmail OAuth callback and store credentials.

    This endpoint is called by Google after the user grants access.
    It exchanges the authorization code for access/refresh tokens and
    stores them securely in the user's profile.

    Args:
        code: Authorization code from Google OAuth
        state: State parameter containing user_id
        redirect_uri: OAuth redirect URI (must match the one used for authorization)
        db: Database session
        gmail_service: Gmail service instance

    Returns:
        Connection status with email address

    Example:
        GET /api/auth/gmail/callback?code=4/0AY0e-g7...&state={"user_id":"123"}

        Response:
        {
            "connected": true,
            "email": "user@gmail.com",
            "connected_at": "2024-01-01T12:00:00Z"
        }
    """
    try:
        # Extract user_id from state
        try:
            state_data = json.loads(state)
            user_id = state_data.get('user_id')
            if not user_id:
                raise ValueError("user_id not found in state")
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Invalid state parameter: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )

        # Exchange code for tokens
        try:
            credentials = await gmail_service.exchange_code_for_tokens(
                code=code,
                redirect_uri=redirect_uri
            )
        except GmailAuthError as e:
            logger.error(f"Failed to exchange code for tokens: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to authenticate with Gmail: {str(e)}"
            )

        # Get user from database
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            logger.error(f"User {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Get Gmail profile to verify and get email address
        try:
            profile = await gmail_service.get_profile(credentials)
            email_address = profile.get('emailAddress')
        except Exception as e:
            logger.warning(f"Failed to get Gmail profile: {str(e)}")
            email_address = None

        # Store credentials in user profile
        user.gmail_credentials = credentials
        await db.commit()
        await db.refresh(user)

        logger.info(f"Successfully connected Gmail for user {user_id} ({email_address})")

        return GmailConnectionStatus(
            connected=True,
            email=email_address,
            connected_at=user.updated_at.isoformat() if user.updated_at else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in OAuth callback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during authentication"
        )


@router.delete("", response_model=MessageResponse)
async def disconnect_gmail(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """Disconnect Gmail integration.

    This endpoint revokes the OAuth token with Google and removes
    the stored credentials from the user's profile.

    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        gmail_service: Gmail service instance

    Returns:
        Success message

    Example:
        DELETE /api/auth/gmail

        Response:
        {
            "message": "Gmail disconnected successfully"
        }
    """
    try:
        # Check if Gmail is connected
        if not current_user.gmail_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gmail is not connected"
            )

        # Get token for revocation (prefer refresh_token, fallback to access_token)
        token = (
            current_user.gmail_credentials.get('refresh_token') or
            current_user.gmail_credentials.get('token')
        )

        # Revoke token with Google
        if token:
            try:
                await gmail_service.revoke_token(token)
                logger.info(f"Revoked Gmail token for user {current_user.id}")
            except Exception as e:
                logger.warning(f"Failed to revoke token (continuing with disconnect): {str(e)}")

        # Remove credentials from user profile
        current_user.gmail_credentials = None
        await db.commit()

        logger.info(f"Disconnected Gmail for user {current_user.id}")

        return MessageResponse(message="Gmail disconnected successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting Gmail: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect Gmail"
        )


@router.get("/status", response_model=GmailConnectionStatus)
async def get_gmail_status(
    current_user: User = Depends(get_current_user),
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """Get Gmail connection status.

    Check if the user has Gmail connected and retrieve the connected email address.

    Args:
        current_user: Authenticated user from JWT token
        gmail_service: Gmail service instance

    Returns:
        Connection status with email if connected

    Example:
        GET /api/auth/gmail/status

        Response:
        {
            "connected": true,
            "email": "user@gmail.com",
            "connected_at": "2024-01-01T12:00:00Z"
        }
    """
    try:
        # Check if credentials exist
        if not current_user.gmail_credentials:
            return GmailConnectionStatus(
                connected=False,
                email=None,
                connected_at=None
            )

        # Try to get profile to verify connection is still valid
        try:
            profile = await gmail_service.get_profile(current_user.gmail_credentials)
            email_address = profile.get('emailAddress')

            return GmailConnectionStatus(
                connected=True,
                email=email_address,
                connected_at=current_user.updated_at.isoformat() if current_user.updated_at else None
            )
        except GmailAuthError as e:
            # Credentials might be expired or revoked
            logger.warning(f"Gmail credentials invalid for user {current_user.id}: {str(e)}")
            return GmailConnectionStatus(
                connected=False,
                email=None,
                connected_at=None
            )

    except Exception as e:
        logger.error(f"Error checking Gmail status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check Gmail status"
        )


@router.post("/refresh", response_model=MessageResponse)
async def refresh_gmail_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    gmail_service: GmailService = Depends(get_gmail_service)
):
    """Manually refresh Gmail access token.

    This endpoint can be used to manually refresh the access token
    before it expires. Note that tokens are automatically refreshed
    when needed by the GmailService.

    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        gmail_service: Gmail service instance

    Returns:
        Success message

    Example:
        POST /api/auth/gmail/refresh

        Response:
        {
            "message": "Token refreshed successfully"
        }
    """
    try:
        # Check if Gmail is connected
        if not current_user.gmail_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gmail is not connected"
            )

        # Get refresh token
        refresh_token = current_user.gmail_credentials.get('refresh_token')
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No refresh token available. Please reconnect Gmail."
            )

        # Refresh the token
        try:
            new_credentials = await gmail_service.refresh_access_token(refresh_token)

            # Update stored credentials
            current_user.gmail_credentials = new_credentials
            await db.commit()

            logger.info(f"Manually refreshed Gmail token for user {current_user.id}")

            return MessageResponse(message="Token refreshed successfully")

        except GmailAuthError as e:
            logger.error(f"Failed to refresh token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to refresh token: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )
