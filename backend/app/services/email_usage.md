# Email Service Usage Guide

## Overview

The `EmailService` provides async email functionality for the GetAnswers application using SMTP (via `aiosmtplib`). It includes beautiful HTML templates for all transactional emails.

## Configuration

Email service requires SMTP configuration in your `.env` file:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@getanswers.co
APP_URL=http://localhost:5073
```

### Using Gmail

1. Enable 2-factor authentication on your Google account
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the app password as `SMTP_PASSWORD`

### Development Mode

If SMTP credentials are not configured, the service will:
- Log email content to console (in development)
- Return `False` for send attempts (in production)

## Available Email Templates

### 1. Magic Link Email

Sends a secure authentication link to users for passwordless login.

```python
from app.services.email import email_service

await email_service.send_magic_link(
    to="user@example.com",
    token="abc123...",
    app_url="http://localhost:5073"  # optional, uses config default
)
```

**Template Features:**
- Clean, modern design
- Prominent CTA button
- 15-minute expiry notice
- Security information

---

### 2. Welcome Email

Sent to new users after registration.

```python
await email_service.send_welcome_email(
    to="user@example.com",
    name="John Doe"
)
```

**Template Features:**
- Friendly greeting
- Feature highlights with checkmarks
- Dashboard CTA button
- GetAnswers branding

---

### 3. Action Notification Email

Alerts users about high-risk AI actions requiring approval.

```python
await email_service.send_action_notification(
    to="user@example.com",
    action_summary="Delete email from John Doe with subject 'Important Meeting'",
    queue_url="http://localhost:5073/queue/action-123",
    action_type="HIGH_RISK"  # or MEDIUM_RISK, LOW_RISK
)
```

**Template Features:**
- Urgent styling with colored badge
- Action summary in highlighted box
- Prominent review button
- Color-coded by risk level

---

### 4. Daily Digest Email

Sends a summary of AI activity and pending actions.

```python
from datetime import datetime

await email_service.send_daily_digest(
    to="user@example.com",
    stats={
        'emails_processed': 42,
        'responses_sent': 15,
        'time_saved_minutes': 120
    },
    pending_actions=[
        {'type': 'DELETE', 'summary': 'Delete spam email'},
        {'type': 'REPLY', 'summary': 'Send reply to meeting request'}
    ],
    date=datetime.utcnow()  # optional, defaults to today
)
```

**Template Features:**
- Colorful stats cards
- Pending actions table
- Efficiency metrics
- Dashboard link

---

## Rate Limiting

Magic link requests are rate-limited to prevent abuse:

- **Limit:** 3 requests per email per hour
- **Storage:** Redis
- **Key:** `magic_link_rate:{email}`
- **Window:** 3600 seconds (1 hour)

The rate limiting is implemented in `/app/api/auth.py` and automatically applied to the `/auth/magic-link` endpoint.

## Error Handling

All email methods return `bool`:
- `True` - Email sent successfully
- `False` - Email failed to send

Errors are logged but don't raise exceptions by default. In critical flows (like magic link), you should check the return value:

```python
email_sent = await email_service.send_magic_link(to, token)
if not email_sent:
    raise HTTPException(
        status_code=500,
        detail="Failed to send magic link email"
    )
```

## Email Templates

All templates include:
- Responsive HTML design
- Inline CSS for email client compatibility
- Plain text fallbacks
- GetAnswers branding
- Mobile-friendly layout

Templates use:
- Modern sans-serif fonts
- Blue primary color (#2563eb)
- Clean, minimal design
- Proper spacing and typography

## Testing

Run the test script to verify email configuration:

```bash
cd backend
python test_email.py
```

The script will:
1. Display current configuration
2. Prompt for a test email address
3. Send all 4 email types
4. Report success/failure for each

## Integration Example

Here's how the email service is integrated in the auth flow:

```python
from app.services.email import email_service
from app.core.redis import get_redis
import logging

logger = logging.getLogger(__name__)

@router.post("/magic-link")
async def request_magic_link(
    request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    # Check rate limit
    if await check_magic_link_rate_limit(request.email, redis_client):
        raise HTTPException(
            status_code=429,
            detail="Too many magic link requests"
        )

    # Create user and magic link...

    # Send email
    try:
        email_sent = await email_service.send_magic_link(
            to=request.email,
            token=token
        )

        if not email_sent:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email"
            )
    except Exception as e:
        logger.error(f"Email error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to send email"
        )

    return {"message": "Check your email for the magic link"}
```

## Future Enhancements

Potential improvements:
- Email template customization per user
- Email delivery tracking
- Bounce handling
- Email verification flow
- Unsubscribe management
- Email analytics
