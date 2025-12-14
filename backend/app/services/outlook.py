"""Microsoft Outlook/Graph API integration service for OAuth and email operations.

This service provides comprehensive Outlook integration including:
- OAuth 2.0 authentication flow with Microsoft identity platform
- Token management and automatic refresh
- Email listing, reading, and sending via Microsoft Graph API
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode
import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class OutlookServiceError(Exception):
    """Base exception for Outlook service errors."""
    pass


class OutlookAuthError(OutlookServiceError):
    """Exception raised for authentication/authorization errors."""
    pass


class OutlookAPIError(OutlookServiceError):
    """Exception raised for Microsoft Graph API errors."""
    pass


class OutlookService:
    """Microsoft Outlook integration service with OAuth 2.0 support.

    This service handles all Outlook operations including authentication
    and email management via Microsoft Graph API.
    """

    # Microsoft Graph API scopes for email access
    SCOPES = [
        'https://graph.microsoft.com/Mail.Read',
        'https://graph.microsoft.com/Mail.ReadWrite',
        'https://graph.microsoft.com/Mail.Send',
        'https://graph.microsoft.com/User.Read',
        'offline_access',  # For refresh tokens
    ]

    # Microsoft OAuth endpoints
    AUTHORITY_BASE = "https://login.microsoftonline.com"
    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None
    ):
        """Initialize Outlook service with OAuth credentials.

        Args:
            client_id: Microsoft OAuth client ID (defaults to settings)
            client_secret: Microsoft OAuth client secret (defaults to settings)
            tenant_id: Microsoft tenant ID (defaults to 'common' for multi-tenant)

        Raises:
            OutlookAuthError: If credentials are not provided or configured
        """
        self.client_id = client_id or settings.MICROSOFT_CLIENT_ID
        self.client_secret = client_secret or settings.MICROSOFT_CLIENT_SECRET
        self.tenant_id = tenant_id or settings.MICROSOFT_TENANT_ID or "common"

        if not self.client_id or not self.client_secret:
            raise OutlookAuthError(
                "Microsoft OAuth credentials not configured. "
                "Please set MICROSOFT_CLIENT_ID and MICROSOFT_CLIENT_SECRET."
            )

    @property
    def authority(self) -> str:
        """Get the OAuth authority URL."""
        return f"{self.AUTHORITY_BASE}/{self.tenant_id}"

    @property
    def authorize_url(self) -> str:
        """Get the OAuth authorization URL."""
        return f"{self.authority}/oauth2/v2.0/authorize"

    @property
    def token_url(self) -> str:
        """Get the OAuth token URL."""
        return f"{self.authority}/oauth2/v2.0/token"

    async def get_authorization_url(self, user_id: str, redirect_uri: str) -> str:
        """Generate Microsoft OAuth authorization URL.

        Args:
            user_id: User ID to include in state parameter
            redirect_uri: OAuth callback URL

        Returns:
            Authorization URL to redirect user to
        """
        import json

        state = json.dumps({"user_id": user_id})

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": " ".join(self.SCOPES),
            "state": state,
            "prompt": "consent",  # Force consent to ensure refresh token
        }

        authorization_url = f"{self.authorize_url}?{urlencode(params)}"
        logger.info(f"Generated Outlook authorization URL for user {user_id}")

        return authorization_url

    async def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> dict:
        """Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: OAuth redirect URI (must match authorization request)

        Returns:
            Dictionary containing token data

        Raises:
            OutlookAuthError: If token exchange fails
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
            "scope": " ".join(self.SCOPES),
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.token_url, data=data)

                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get("error_description", "Token exchange failed")
                    logger.error(f"Outlook token exchange failed: {error_msg}")
                    raise OutlookAuthError(error_msg)

                token_data = response.json()

                # Build credentials dict
                credentials = {
                    "token": token_data.get("access_token"),
                    "refresh_token": token_data.get("refresh_token"),
                    "token_type": token_data.get("token_type", "Bearer"),
                    "expires_at": (
                        datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
                    ).isoformat(),
                    "scopes": token_data.get("scope", "").split(" "),
                }

                logger.info("Successfully exchanged code for Outlook tokens")
                return credentials

            except httpx.HTTPError as e:
                logger.error(f"HTTP error during token exchange: {str(e)}")
                raise OutlookAuthError(f"Failed to exchange code: {str(e)}")

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token.

        Args:
            refresh_token: OAuth refresh token

        Returns:
            Dictionary containing new token data

        Raises:
            OutlookAuthError: If token refresh fails
        """
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
            "scope": " ".join(self.SCOPES),
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.token_url, data=data)

                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get("error_description", "Token refresh failed")
                    logger.error(f"Outlook token refresh failed: {error_msg}")
                    raise OutlookAuthError(error_msg)

                token_data = response.json()

                credentials = {
                    "token": token_data.get("access_token"),
                    "refresh_token": token_data.get("refresh_token", refresh_token),
                    "token_type": token_data.get("token_type", "Bearer"),
                    "expires_at": (
                        datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
                    ).isoformat(),
                    "scopes": token_data.get("scope", "").split(" "),
                }

                logger.info("Successfully refreshed Outlook access token")
                return credentials

            except httpx.HTTPError as e:
                logger.error(f"HTTP error during token refresh: {str(e)}")
                raise OutlookAuthError(f"Failed to refresh token: {str(e)}")

    async def get_profile(self, credentials: dict) -> dict:
        """Get user profile from Microsoft Graph API.

        Args:
            credentials: OAuth credentials dictionary

        Returns:
            User profile data including email

        Raises:
            OutlookAuthError: If credentials are invalid
            OutlookAPIError: If API request fails
        """
        token = credentials.get("token")
        if not token:
            raise OutlookAuthError("No access token in credentials")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.GRAPH_API_BASE}/me",
                    headers=headers
                )

                if response.status_code == 401:
                    raise OutlookAuthError("Access token expired or invalid")

                if response.status_code != 200:
                    raise OutlookAPIError(f"Failed to get profile: {response.text}")

                profile = response.json()
                return {
                    "emailAddress": profile.get("mail") or profile.get("userPrincipalName"),
                    "displayName": profile.get("displayName"),
                    "id": profile.get("id"),
                }

            except httpx.HTTPError as e:
                logger.error(f"HTTP error getting profile: {str(e)}")
                raise OutlookAPIError(f"Failed to get profile: {str(e)}")

    async def revoke_token(self, token: str) -> None:
        """Revoke OAuth token.

        Note: Microsoft doesn't have a standard revocation endpoint.
        The token will expire naturally. For security, clear stored credentials.

        Args:
            token: Access or refresh token to revoke
        """
        # Microsoft Graph API doesn't support token revocation in the same way as Google
        # Best practice is to just clear the stored credentials
        logger.info("Token revocation requested - credentials should be cleared from storage")


def get_outlook_service() -> OutlookService:
    """Factory function to create OutlookService instance.

    Returns:
        Configured OutlookService instance

    Raises:
        OutlookAuthError: If service cannot be initialized
    """
    return OutlookService()
