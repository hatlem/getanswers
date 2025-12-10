# Gmail OAuth Integration - Implementation Guide

This document describes the Gmail OAuth integration implementation for the GetAnswers project.

## Overview

The Gmail integration provides comprehensive OAuth 2.0 authentication and email management capabilities including:

- OAuth 2.0 authorization flow
- Automatic token refresh
- Secure credential storage
- Email operations (read, send, draft)
- Push notifications support
- Error handling and rate limiting

## Architecture

### Components

1. **GmailService** (`backend/app/services/gmail.py`)
   - Core service handling Gmail API operations
   - OAuth token management
   - Email CRUD operations
   - Automatic credential refresh

2. **Gmail API Endpoints** (`backend/app/api/gmail.py`)
   - `/api/auth/gmail` - Get OAuth authorization URL
   - `/api/auth/gmail/callback` - Handle OAuth callback
   - `/api/auth/gmail/status` - Check connection status
   - `/api/auth/gmail/refresh` - Manually refresh token
   - `DELETE /api/auth/gmail` - Disconnect Gmail

3. **Dependencies** (`backend/app/services/dependencies.py`)
   - `get_gmail_service()` - FastAPI dependency for GmailService injection

4. **Configuration** (`backend/app/core/config.py`)
   - `GMAIL_CLIENT_ID` - Google OAuth Client ID
   - `GMAIL_CLIENT_SECRET` - Google OAuth Client Secret

## Setup

### 1. Google Cloud Console Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable Gmail API:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click "Enable"
4. Create OAuth 2.0 credentials:
   - Navigate to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - Development: `http://localhost:5073/gmail/callback`
     - Production: `https://yourdomain.com/gmail/callback`
   - Copy Client ID and Client Secret

### 2. Environment Configuration

Add to your `.env` file:

```bash
# Gmail OAuth Configuration
GMAIL_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret-here
```

### 3. Install Dependencies

Dependencies are already included in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key packages:
- `google-api-python-client` - Gmail API client
- `google-auth-oauthlib` - OAuth 2.0 flow
- `google-auth-httplib2` - HTTP transport for Google Auth

## Usage

### Frontend OAuth Flow

1. **Initiate Authorization**

```typescript
// Get authorization URL
const response = await fetch('/api/auth/gmail?redirect_uri=http://localhost:5073/gmail/callback', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const { authorization_url } = await response.json();

// Redirect user to Google consent screen
window.location.href = authorization_url;
```

2. **Handle Callback**

```typescript
// After user grants access, Google redirects to your callback URL
// Extract code and state from URL parameters
const params = new URLSearchParams(window.location.search);
const code = params.get('code');
const state = params.get('state');

// Exchange code for tokens (handled automatically by backend)
const response = await fetch(`/api/auth/gmail/callback?code=${code}&state=${state}&redirect_uri=http://localhost:5073/gmail/callback`);
const status = await response.json();

if (status.connected) {
  console.log(`Gmail connected: ${status.email}`);
}
```

3. **Check Connection Status**

```typescript
const response = await fetch('/api/auth/gmail/status', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const status = await response.json();

if (status.connected) {
  console.log(`Connected to: ${status.email}`);
} else {
  console.log('Gmail not connected');
}
```

4. **Disconnect Gmail**

```typescript
const response = await fetch('/api/auth/gmail', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
const result = await response.json();
console.log(result.message); // "Gmail disconnected successfully"
```

### Backend Service Usage

```python
from app.services import GmailService
from app.services.dependencies import get_gmail_service

# Using dependency injection in FastAPI
@router.get("/emails")
async def get_emails(
    gmail: GmailService = Depends(get_gmail_service),
    current_user: User = Depends(get_current_user)
):
    # Get user's Gmail messages
    result = await gmail.get_messages(
        credentials=current_user.gmail_credentials,
        max_results=50,
        query="is:unread"
    )

    return result

# Send an email
@router.post("/send")
async def send_email(
    gmail: GmailService = Depends(get_gmail_service),
    current_user: User = Depends(get_current_user)
):
    result = await gmail.send_message(
        credentials=current_user.gmail_credentials,
        to="recipient@example.com",
        subject="Hello from GetAnswers",
        body="This is an automated email."
    )

    return {"message_id": result['id']}
```

## GmailService API Reference

### OAuth Methods

#### `get_authorization_url(user_id: str, redirect_uri: str) -> str`
Generate OAuth authorization URL for user consent.

#### `exchange_code_for_tokens(code: str, redirect_uri: str) -> dict`
Exchange authorization code for access and refresh tokens.

#### `refresh_access_token(refresh_token: str) -> dict`
Refresh access token using refresh token.

#### `revoke_token(token: str) -> bool`
Revoke OAuth token to disconnect Gmail access.

### Email Methods

#### `get_messages(credentials: dict, max_results: int = 50, query: str = None, page_token: str = None) -> dict`
Retrieve list of messages from Gmail.

**Parameters:**
- `credentials` - OAuth credentials dictionary
- `max_results` - Maximum number of messages (1-500)
- `query` - Gmail search query (e.g., "is:unread", "from:example@gmail.com")
- `page_token` - Token for pagination

**Returns:**
```python
{
    'messages': [...],
    'nextPageToken': '...',
    'resultSizeEstimate': 100
}
```

#### `get_message(credentials: dict, message_id: str) -> dict`
Retrieve full message details by ID.

#### `get_thread(credentials: dict, thread_id: str) -> dict`
Retrieve email thread by ID.

#### `send_message(credentials: dict, to: str, subject: str, body: str, thread_id: str = None, message_type: str = 'plain') -> dict`
Send an email message.

**Parameters:**
- `message_type` - 'plain' or 'html'
- `thread_id` - Optional thread ID for replies

#### `create_draft(credentials: dict, to: str, subject: str, body: str, thread_id: str = None, message_type: str = 'plain') -> dict`
Create a draft email.

### Watch Methods (Push Notifications)

#### `watch_inbox(credentials: dict, topic_name: str) -> dict`
Set up push notifications for inbox changes.

**Requirements:**
- Google Cloud Pub/Sub topic configured
- Topic name format: `projects/{project}/topics/{topic}`

#### `stop_watch(credentials: dict) -> bool`
Stop push notifications for the user.

### Utility Methods

#### `get_profile(credentials: dict) -> dict`
Get user's Gmail profile information including email address.

## Error Handling

The service includes comprehensive error handling:

### Exception Types

- `GmailServiceError` - Base exception for Gmail service errors
- `GmailAuthError` - Authentication/authorization errors
- `GmailAPIError` - Gmail API errors
- `GmailRateLimitError` - Rate limit exceeded

### Automatic Token Refresh

The service automatically refreshes expired access tokens using the refresh token. This happens transparently when:

1. Token is expired (checked before each API call)
2. Access token is expired but refresh token is valid
3. User doesn't need to re-authenticate

### Rate Limiting

Gmail API has quotas and rate limits:
- 250 quota units per user per second
- 1 billion quota units per day

The service catches rate limit errors and raises `GmailRateLimitError` for proper handling.

## Security Considerations

### Credential Storage

- Credentials are stored in `User.gmail_credentials` (JSON field)
- **Important:** Consider encrypting this field in production
- Never log or expose credentials in API responses

### OAuth Scopes

The service requests these Gmail scopes:

```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',      # Read emails
    'https://www.googleapis.com/auth/gmail.send',          # Send emails
    'https://www.googleapis.com/auth/gmail.compose',       # Create drafts
    'https://www.googleapis.com/auth/gmail.modify',        # Modify emails
    'https://mail.google.com/',                            # Full Gmail access
]
```

**Note:** You can reduce scopes based on your needs to minimize permissions.

### Token Expiration

- Access tokens expire after 1 hour
- Refresh tokens are long-lived (can be revoked by user)
- Always include `access_type='offline'` to get refresh token
- Use `prompt='consent'` to ensure refresh token is returned

## Testing

### Manual Testing Steps

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload
```

2. Visit API documentation:
```
http://localhost:8000/docs
```

3. Test OAuth flow:
   - Authenticate a user (get access token)
   - Call `/api/auth/gmail` with redirect_uri
   - Visit the returned authorization_url
   - Grant permissions
   - Handle the callback (automatic in production)

### Integration with Triage Service

The placeholder `GmailService` in `triage.py` should be replaced with the real implementation:

```python
# In triage.py, replace:
# from .triage import GmailService

# With:
from .gmail import GmailService

# Then update TriageService to use the real Gmail service methods
```

## Troubleshooting

### Common Issues

1. **"Gmail OAuth credentials not configured"**
   - Ensure `GMAIL_CLIENT_ID` and `GMAIL_CLIENT_SECRET` are set in `.env`
   - Restart the server after updating environment variables

2. **"Invalid grant" error during token exchange**
   - Authorization code has expired (valid for 10 minutes)
   - User needs to re-authenticate
   - Ensure redirect_uri matches exactly

3. **"Token has been expired or revoked"**
   - User has revoked access in Google Account settings
   - User needs to reconnect Gmail
   - Call `/api/auth/gmail` to restart OAuth flow

4. **Rate limit errors**
   - Implement exponential backoff
   - Cache frequently accessed data
   - Consider batch operations where possible

## Next Steps

1. **Implement Message Parsing**
   - Create helper functions to parse Gmail message format
   - Extract plain text from multipart MIME messages
   - Handle attachments

2. **Add Webhook Handler**
   - Set up Cloud Pub/Sub topic
   - Create endpoint to receive push notifications
   - Process incoming notifications for real-time sync

3. **Enhance Security**
   - Add credential encryption at rest
   - Implement token rotation policy
   - Add audit logging for Gmail operations

4. **Update Triage Service**
   - Replace placeholder GmailService with real implementation
   - Implement message fetching and parsing
   - Add sync scheduling

## Resources

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [OAuth 2.0 Scopes for Google APIs](https://developers.google.com/identity/protocols/oauth2/scopes)

## License

Part of the GetAnswers project.
