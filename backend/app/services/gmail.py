"""Gmail API integration service for OAuth and email operations.

This service provides comprehensive Gmail integration including:
- OAuth 2.0 authentication flow
- Token management and automatic refresh
- Email listing, reading, and sending
- Draft creation
- Push notification subscriptions

Dependencies:
    - google-auth-oauthlib: OAuth 2.0 flow
    - google-api-python-client: Gmail API client
    - google-auth: Credentials management
"""

import base64
import json
import logging
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List, Any
from urllib.parse import urlencode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings

logger = logging.getLogger(__name__)


class GmailServiceError(Exception):
    """Base exception for Gmail service errors."""
    pass


class GmailAuthError(GmailServiceError):
    """Exception raised for authentication/authorization errors."""
    pass


class GmailAPIError(GmailServiceError):
    """Exception raised for Gmail API errors."""
    pass


class GmailRateLimitError(GmailServiceError):
    """Exception raised when Gmail API rate limit is exceeded."""
    pass


class GmailService:
    """Gmail API integration service with OAuth 2.0 support.

    This service handles all Gmail operations including authentication,
    email management, and push notifications.

    Attributes:
        SCOPES: List of Gmail API scopes required for operations
        client_id: Google OAuth client ID
        client_secret: Google OAuth client secret
    """

    # Gmail API scopes - requesting full access for comprehensive email management
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',      # Read emails
        'https://www.googleapis.com/auth/gmail.send',          # Send emails
        'https://www.googleapis.com/auth/gmail.compose',       # Create drafts
        'https://www.googleapis.com/auth/gmail.modify',        # Modify emails (labels, etc.)
        'https://mail.google.com/',                            # Full Gmail access
    ]

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize Gmail service with OAuth credentials.

        Args:
            client_id: Google OAuth client ID (defaults to settings)
            client_secret: Google OAuth client secret (defaults to settings)

        Raises:
            GmailAuthError: If credentials are not provided or configured
        """
        self.client_id = client_id or settings.GMAIL_CLIENT_ID
        self.client_secret = client_secret or settings.GMAIL_CLIENT_SECRET

        if not self.client_id or not self.client_secret:
            raise GmailAuthError(
                "Gmail OAuth credentials not configured. "
                "Please set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET."
            )

    def _get_oauth_flow(self, redirect_uri: str) -> Flow:
        """Create OAuth 2.0 flow for authorization.

        Args:
            redirect_uri: OAuth callback URL

        Returns:
            Configured OAuth flow instance
        """
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        }

        flow = Flow.from_client_config(
            client_config,
            scopes=self.SCOPES,
            redirect_uri=redirect_uri
        )

        return flow

    def _credentials_from_dict(self, creds_dict: dict) -> Credentials:
        """Convert credentials dictionary to Credentials object.

        Args:
            creds_dict: Dictionary containing OAuth credentials

        Returns:
            Google OAuth Credentials object
        """
        return Credentials(
            token=creds_dict.get('token'),
            refresh_token=creds_dict.get('refresh_token'),
            token_uri='https://oauth2.googleapis.com/token',
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=creds_dict.get('scopes', self.SCOPES)
        )

    def _credentials_to_dict(self, creds: Credentials) -> dict:
        """Convert Credentials object to dictionary for storage.

        Args:
            creds: Google OAuth Credentials object

        Returns:
            Dictionary containing credential data
        """
        return {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
            'expiry': creds.expiry.isoformat() if creds.expiry else None
        }

    async def get_authorization_url(self, user_id: str, redirect_uri: str) -> str:
        """Generate OAuth authorization URL for user consent.

        Args:
            user_id: User ID to include in state parameter
            redirect_uri: OAuth callback URL

        Returns:
            Authorization URL for user to grant access

        Example:
            url = await gmail_service.get_authorization_url(
                user_id="123",
                redirect_uri="http://localhost:8000/api/auth/gmail/callback"
            )
        """
        try:
            flow = self._get_oauth_flow(redirect_uri)

            # Include user_id in state for security and session tracking
            state = json.dumps({'user_id': user_id})

            authorization_url, _ = flow.authorization_url(
                access_type='offline',  # Get refresh token
                include_granted_scopes='true',  # Incremental authorization
                prompt='consent',  # Force consent screen to get refresh token
                state=state
            )

            logger.info(f"Generated authorization URL for user {user_id}")
            return authorization_url

        except Exception as e:
            logger.error(f"Error generating authorization URL: {str(e)}")
            raise GmailAuthError(f"Failed to generate authorization URL: {str(e)}")

    async def exchange_code_for_tokens(self, code: str, redirect_uri: str) -> dict:
        """Exchange authorization code for access and refresh tokens.

        Args:
            code: Authorization code from OAuth callback
            redirect_uri: OAuth callback URL (must match the one used for authorization)

        Returns:
            Dictionary containing OAuth credentials

        Raises:
            GmailAuthError: If token exchange fails

        Example:
            credentials = await gmail_service.exchange_code_for_tokens(
                code="4/0AY0e-g7...",
                redirect_uri="http://localhost:8000/api/auth/gmail/callback"
            )
        """
        try:
            flow = self._get_oauth_flow(redirect_uri)
            flow.fetch_token(code=code)

            credentials = flow.credentials
            creds_dict = self._credentials_to_dict(credentials)

            logger.info("Successfully exchanged authorization code for tokens")
            return creds_dict

        except Exception as e:
            logger.error(f"Error exchanging authorization code: {str(e)}")
            raise GmailAuthError(f"Failed to exchange authorization code: {str(e)}")

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """Refresh access token using refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Updated credentials dictionary with new access token

        Raises:
            GmailAuthError: If token refresh fails

        Example:
            new_credentials = await gmail_service.refresh_access_token(
                refresh_token="1//0gHZBv..."
            )
        """
        try:
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=self.SCOPES
            )

            # Refresh the token
            credentials.refresh(Request())

            creds_dict = self._credentials_to_dict(credentials)

            logger.info("Successfully refreshed access token")
            return creds_dict

        except Exception as e:
            logger.error(f"Error refreshing access token: {str(e)}")
            raise GmailAuthError(f"Failed to refresh access token: {str(e)}")

    async def revoke_token(self, token: str) -> bool:
        """Revoke OAuth token to disconnect Gmail access.

        Args:
            token: Access token or refresh token to revoke

        Returns:
            True if revocation successful

        Raises:
            GmailAuthError: If revocation fails

        Example:
            success = await gmail_service.revoke_token(token)
        """
        try:
            import requests

            response = requests.post(
                'https://oauth2.googleapis.com/revoke',
                params={'token': token},
                headers={'content-type': 'application/x-www-form-urlencoded'}
            )

            if response.status_code == 200:
                logger.info("Successfully revoked token")
                return True
            else:
                logger.warning(f"Token revocation returned status {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
            raise GmailAuthError(f"Failed to revoke token: {str(e)}")

    def _ensure_valid_credentials(self, credentials: dict) -> Credentials:
        """Ensure credentials are valid and refresh if necessary.

        Args:
            credentials: Credentials dictionary

        Returns:
            Valid Credentials object

        Raises:
            GmailAuthError: If credentials are invalid or refresh fails
        """
        creds = self._credentials_from_dict(credentials)

        # Check if credentials are expired and refresh if needed
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Auto-refreshed expired access token")
            except Exception as e:
                logger.error(f"Error auto-refreshing token: {str(e)}")
                raise GmailAuthError(f"Failed to refresh expired token: {str(e)}")

        return creds

    def _build_gmail_service(self, credentials: dict):
        """Build Gmail API service with credentials.

        Args:
            credentials: OAuth credentials dictionary

        Returns:
            Gmail API service object
        """
        creds = self._ensure_valid_credentials(credentials)
        service = build('gmail', 'v1', credentials=creds)
        return service

    async def get_messages(
        self,
        credentials: dict,
        max_results: int = 50,
        query: str = None,
        page_token: str = None
    ) -> dict:
        """Retrieve list of messages from Gmail.

        Args:
            credentials: OAuth credentials dictionary
            max_results: Maximum number of messages to return (1-500)
            query: Gmail search query (e.g., "is:unread", "from:example@gmail.com")
            page_token: Token for pagination

        Returns:
            Dictionary containing messages list and next page token

        Raises:
            GmailAPIError: If API request fails
            GmailRateLimitError: If rate limit is exceeded

        Example:
            result = await gmail_service.get_messages(
                credentials=user.gmail_credentials,
                max_results=10,
                query="is:unread"
            )
            messages = result['messages']
            next_page = result.get('nextPageToken')
        """
        try:
            service = self._build_gmail_service(credentials)

            # Build request parameters
            params = {
                'userId': 'me',
                'maxResults': min(max_results, 500),
            }

            if query:
                params['q'] = query

            if page_token:
                params['pageToken'] = page_token

            # Execute request
            results = service.users().messages().list(**params).execute()

            messages = results.get('messages', [])
            next_page_token = results.get('nextPageToken')

            logger.info(f"Retrieved {len(messages)} messages")

            return {
                'messages': messages,
                'nextPageToken': next_page_token,
                'resultSizeEstimate': results.get('resultSizeEstimate', 0)
            }

        except HttpError as e:
            if e.resp.status == 429:
                logger.error("Gmail API rate limit exceeded")
                raise GmailRateLimitError("Rate limit exceeded. Please try again later.")
            logger.error(f"Gmail API error: {str(e)}")
            raise GmailAPIError(f"Failed to retrieve messages: {str(e)}")
        except Exception as e:
            logger.error(f"Error retrieving messages: {str(e)}")
            raise GmailAPIError(f"Failed to retrieve messages: {str(e)}")

    async def get_message(self, credentials: dict, message_id: str) -> dict:
        """Retrieve full message details by ID.

        Args:
            credentials: OAuth credentials dictionary
            message_id: Gmail message ID

        Returns:
            Complete message object with headers, body, and metadata

        Raises:
            GmailAPIError: If API request fails

        Example:
            message = await gmail_service.get_message(
                credentials=user.gmail_credentials,
                message_id="18abc123def456"
            )
            subject = next(h['value'] for h in message['payload']['headers']
                          if h['name'] == 'Subject')
        """
        try:
            service = self._build_gmail_service(credentials)

            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'  # Get full message including body
            ).execute()

            logger.info(f"Retrieved message {message_id}")
            return message

        except HttpError as e:
            if e.resp.status == 404:
                raise GmailAPIError(f"Message {message_id} not found")
            logger.error(f"Gmail API error: {str(e)}")
            raise GmailAPIError(f"Failed to retrieve message: {str(e)}")
        except Exception as e:
            logger.error(f"Error retrieving message: {str(e)}")
            raise GmailAPIError(f"Failed to retrieve message: {str(e)}")

    async def get_thread(self, credentials: dict, thread_id: str) -> dict:
        """Retrieve email thread by ID.

        Args:
            credentials: OAuth credentials dictionary
            thread_id: Gmail thread ID

        Returns:
            Thread object containing all messages in the thread

        Raises:
            GmailAPIError: If API request fails

        Example:
            thread = await gmail_service.get_thread(
                credentials=user.gmail_credentials,
                thread_id="18abc123def456"
            )
            messages = thread['messages']
        """
        try:
            service = self._build_gmail_service(credentials)

            thread = service.users().threads().get(
                userId='me',
                id=thread_id,
                format='full'
            ).execute()

            logger.info(f"Retrieved thread {thread_id} with {len(thread.get('messages', []))} messages")
            return thread

        except HttpError as e:
            if e.resp.status == 404:
                raise GmailAPIError(f"Thread {thread_id} not found")
            logger.error(f"Gmail API error: {str(e)}")
            raise GmailAPIError(f"Failed to retrieve thread: {str(e)}")
        except Exception as e:
            logger.error(f"Error retrieving thread: {str(e)}")
            raise GmailAPIError(f"Failed to retrieve thread: {str(e)}")

    def _create_message(
        self,
        to: str,
        subject: str,
        body: str,
        thread_id: str = None,
        message_type: str = 'plain'
    ) -> dict:
        """Create email message in RFC 2822 format.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            thread_id: Thread ID for reply
            message_type: 'plain' or 'html'

        Returns:
            Message dictionary ready for Gmail API
        """
        if message_type == 'html':
            message = MIMEText(body, 'html')
        else:
            message = MIMEText(body, 'plain')

        message['to'] = to
        message['subject'] = subject

        # If replying to a thread, add headers
        if thread_id:
            message['References'] = thread_id
            message['In-Reply-To'] = thread_id

        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        body = {'raw': raw_message}
        if thread_id:
            body['threadId'] = thread_id

        return body

    async def send_message(
        self,
        credentials: dict,
        to: str,
        subject: str,
        body: str,
        thread_id: str = None,
        message_type: str = 'plain'
    ) -> dict:
        """Send an email message.

        Args:
            credentials: OAuth credentials dictionary
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            thread_id: Optional thread ID to reply to
            message_type: 'plain' or 'html' (default: 'plain')

        Returns:
            Sent message object with ID and thread ID

        Raises:
            GmailAPIError: If sending fails

        Example:
            result = await gmail_service.send_message(
                credentials=user.gmail_credentials,
                to="recipient@example.com",
                subject="Hello",
                body="This is a test email"
            )
            message_id = result['id']
        """
        try:
            service = self._build_gmail_service(credentials)

            message = self._create_message(to, subject, body, thread_id, message_type)

            sent_message = service.users().messages().send(
                userId='me',
                body=message
            ).execute()

            logger.info(f"Sent message {sent_message['id']} to {to}")
            return sent_message

        except HttpError as e:
            logger.error(f"Gmail API error sending message: {str(e)}")
            raise GmailAPIError(f"Failed to send message: {str(e)}")
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            raise GmailAPIError(f"Failed to send message: {str(e)}")

    async def create_draft(
        self,
        credentials: dict,
        to: str,
        subject: str,
        body: str,
        thread_id: str = None,
        message_type: str = 'plain'
    ) -> dict:
        """Create a draft email.

        Args:
            credentials: OAuth credentials dictionary
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            thread_id: Optional thread ID to reply to
            message_type: 'plain' or 'html' (default: 'plain')

        Returns:
            Draft object with ID and message

        Raises:
            GmailAPIError: If draft creation fails

        Example:
            draft = await gmail_service.create_draft(
                credentials=user.gmail_credentials,
                to="recipient@example.com",
                subject="Draft Subject",
                body="Draft body content"
            )
            draft_id = draft['id']
        """
        try:
            service = self._build_gmail_service(credentials)

            message = self._create_message(to, subject, body, thread_id, message_type)

            draft = service.users().drafts().create(
                userId='me',
                body={'message': message}
            ).execute()

            logger.info(f"Created draft {draft['id']}")
            return draft

        except HttpError as e:
            logger.error(f"Gmail API error creating draft: {str(e)}")
            raise GmailAPIError(f"Failed to create draft: {str(e)}")
        except Exception as e:
            logger.error(f"Error creating draft: {str(e)}")
            raise GmailAPIError(f"Failed to create draft: {str(e)}")

    async def watch_inbox(self, credentials: dict, topic_name: str) -> dict:
        """Set up push notifications for inbox changes.

        This enables real-time notifications when new emails arrive.
        Requires a Google Cloud Pub/Sub topic to be set up.

        Args:
            credentials: OAuth credentials dictionary
            topic_name: Full Pub/Sub topic name (projects/{project}/topics/{topic})

        Returns:
            Watch response with historyId and expiration

        Raises:
            GmailAPIError: If watch setup fails

        Example:
            watch = await gmail_service.watch_inbox(
                credentials=user.gmail_credentials,
                topic_name="projects/my-project/topics/gmail-push"
            )
            history_id = watch['historyId']
            expires = watch['expiration']
        """
        try:
            service = self._build_gmail_service(credentials)

            request_body = {
                'topicName': topic_name,
                'labelIds': ['INBOX']  # Watch inbox only
            }

            watch_response = service.users().watch(
                userId='me',
                body=request_body
            ).execute()

            logger.info(f"Set up inbox watch with expiration {watch_response.get('expiration')}")
            return watch_response

        except HttpError as e:
            logger.error(f"Gmail API error setting up watch: {str(e)}")
            raise GmailAPIError(f"Failed to set up inbox watch: {str(e)}")
        except Exception as e:
            logger.error(f"Error setting up watch: {str(e)}")
            raise GmailAPIError(f"Failed to set up inbox watch: {str(e)}")

    async def stop_watch(self, credentials: dict) -> bool:
        """Stop push notifications for the user.

        Args:
            credentials: OAuth credentials dictionary

        Returns:
            True if successfully stopped

        Raises:
            GmailAPIError: If stop operation fails

        Example:
            success = await gmail_service.stop_watch(
                credentials=user.gmail_credentials
            )
        """
        try:
            service = self._build_gmail_service(credentials)

            service.users().stop(userId='me').execute()

            logger.info("Stopped inbox watch")
            return True

        except HttpError as e:
            logger.error(f"Gmail API error stopping watch: {str(e)}")
            raise GmailAPIError(f"Failed to stop inbox watch: {str(e)}")
        except Exception as e:
            logger.error(f"Error stopping watch: {str(e)}")
            raise GmailAPIError(f"Failed to stop inbox watch: {str(e)}")

    async def get_profile(self, credentials: dict) -> dict:
        """Get user's Gmail profile information.

        Args:
            credentials: OAuth credentials dictionary

        Returns:
            Profile with email address and other metadata

        Raises:
            GmailAPIError: If profile retrieval fails

        Example:
            profile = await gmail_service.get_profile(
                credentials=user.gmail_credentials
            )
            email_address = profile['emailAddress']
        """
        try:
            service = self._build_gmail_service(credentials)

            profile = service.users().getProfile(userId='me').execute()

            logger.info(f"Retrieved profile for {profile.get('emailAddress')}")
            return profile

        except HttpError as e:
            logger.error(f"Gmail API error getting profile: {str(e)}")
            raise GmailAPIError(f"Failed to get profile: {str(e)}")
        except Exception as e:
            logger.error(f"Error getting profile: {str(e)}")
            raise GmailAPIError(f"Failed to get profile: {str(e)}")
