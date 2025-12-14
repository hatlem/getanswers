"""Microsoft Outlook OAuth integration API endpoints.

This module provides endpoints for:
- Outlook OAuth authorization flow
- Token management and refresh
- Outlook disconnection
"""

import json
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.services.outlook import OutlookService, OutlookAuthError, OutlookAPIError, get_outlook_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/outlook", tags=["Outlook OAuth"])


# Request/Response Schemas
class AuthorizationUrlResponse(BaseModel):
    """Response containing Outlook OAuth authorization URL."""
    authorization_url: str = Field(description="URL to redirect user to for Outlook authorization")
    user_id: UUID = Field(description="User ID for tracking")


class OutlookConnectionStatus(BaseModel):
    """Outlook connection status response."""
    connected: bool = Field(description="Whether Outlook is connected")
    email: Optional[str] = Field(None, description="Connected Outlook email address")
    connected_at: Optional[str] = Field(None, description="When the connection was established")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


@router.get("", response_model=AuthorizationUrlResponse)
async def get_outlook_authorization_url(
    redirect_uri: str = Query(..., description="OAuth redirect URI (callback URL)"),
    current_user: User = Depends(get_current_user),
    outlook_service: OutlookService = Depends(get_outlook_service)
):
    """Generate Microsoft Outlook OAuth authorization URL.

    This endpoint starts the OAuth flow by generating an authorization URL
    that the client should redirect the user to for granting Outlook access.

    Args:
        redirect_uri: The callback URL where Microsoft will redirect after authorization
        current_user: Authenticated user from JWT token
        outlook_service: Outlook service instance

    Returns:
        Authorization URL and user ID
    """
    try:
        authorization_url = await outlook_service.get_authorization_url(
            user_id=str(current_user.id),
            redirect_uri=redirect_uri
        )

        logger.info(f"Generated Outlook authorization URL for user {current_user.id}")

        return AuthorizationUrlResponse(
            authorization_url=authorization_url,
            user_id=current_user.id
        )

    except OutlookAuthError as e:
        logger.error(f"Outlook auth error: {str(e)}")
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


@router.get("/callback", response_model=OutlookConnectionStatus)
async def outlook_oauth_callback(
    code: str = Query(..., description="Authorization code from Microsoft"),
    state: str = Query(..., description="State parameter containing user_id"),
    redirect_uri: str = Query(..., description="OAuth redirect URI (must match authorization request)"),
    db: AsyncSession = Depends(get_db),
    outlook_service: OutlookService = Depends(get_outlook_service)
):
    """Handle Outlook OAuth callback and store credentials.

    This endpoint is called by Microsoft after the user grants access.
    It exchanges the authorization code for access/refresh tokens and
    stores them securely in the user's profile.

    Args:
        code: Authorization code from Microsoft OAuth
        state: State parameter containing user_id
        redirect_uri: OAuth redirect URI (must match the one used for authorization)
        db: Database session
        outlook_service: Outlook service instance

    Returns:
        Connection status with email address
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
            credentials = await outlook_service.exchange_code_for_tokens(
                code=code,
                redirect_uri=redirect_uri
            )
        except OutlookAuthError as e:
            logger.error(f"Failed to exchange code for tokens: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to authenticate with Outlook: {str(e)}"
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

        # Get Outlook profile to verify and get email address
        try:
            profile = await outlook_service.get_profile(credentials)
            email_address = profile.get('emailAddress')
        except Exception as e:
            logger.warning(f"Failed to get Outlook profile: {str(e)}")
            email_address = None

        # Store credentials in user profile
        user.outlook_credentials = credentials
        user.email_provider = 'outlook'
        await db.commit()
        await db.refresh(user)

        logger.info(f"Successfully connected Outlook for user {user_id} ({email_address})")

        return OutlookConnectionStatus(
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
async def disconnect_outlook(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    outlook_service: OutlookService = Depends(get_outlook_service)
):
    """Disconnect Outlook integration.

    This endpoint removes the stored credentials from the user's profile.

    Args:
        current_user: Authenticated user from JWT token
        db: Database session
        outlook_service: Outlook service instance

    Returns:
        Success message
    """
    try:
        # Check if Outlook is connected
        if not current_user.outlook_credentials:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Outlook is not connected"
            )

        # Remove credentials from user profile
        current_user.outlook_credentials = None
        if current_user.email_provider == 'outlook':
            current_user.email_provider = None
        await db.commit()

        logger.info(f"Disconnected Outlook for user {current_user.id}")

        return MessageResponse(message="Outlook disconnected successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disconnecting Outlook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disconnect Outlook"
        )


@router.get("/status", response_model=OutlookConnectionStatus)
async def get_outlook_status(
    current_user: User = Depends(get_current_user),
    outlook_service: OutlookService = Depends(get_outlook_service)
):
    """Get Outlook connection status.

    Check if the user has Outlook connected and retrieve the connected email address.

    Args:
        current_user: Authenticated user from JWT token
        outlook_service: Outlook service instance

    Returns:
        Connection status with email if connected
    """
    try:
        # Check if credentials exist
        if not current_user.outlook_credentials:
            return OutlookConnectionStatus(
                connected=False,
                email=None,
                connected_at=None
            )

        # Try to get profile to verify connection is still valid
        try:
            profile = await outlook_service.get_profile(current_user.outlook_credentials)
            email_address = profile.get('emailAddress')

            return OutlookConnectionStatus(
                connected=True,
                email=email_address,
                connected_at=current_user.updated_at.isoformat() if current_user.updated_at else None
            )
        except OutlookAuthError as e:
            # Credentials might be expired or revoked
            logger.warning(f"Outlook credentials invalid for user {current_user.id}: {str(e)}")
            return OutlookConnectionStatus(
                connected=False,
                email=None,
                connected_at=None
            )

    except Exception as e:
        logger.error(f"Error checking Outlook status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check Outlook status"
        )
