"""Test script for email service functionality."""

import asyncio
from datetime import datetime
from app.services.email import EmailService
from app.core.config import settings


async def test_email_service():
    """Test email service with sample data."""
    email_service = EmailService()

    print("=" * 60)
    print("Testing GetAnswers Email Service")
    print("=" * 60)
    print()

    # Test configuration
    print("Email Configuration:")
    print(f"  SMTP Host: {email_service.host}")
    print(f"  SMTP Port: {email_service.port}")
    print(f"  From Email: {email_service.from_email}")
    print(f"  SMTP User: {email_service.username or 'Not configured'}")
    print(f"  App URL: {email_service.app_url}")
    print(f"  Environment: {settings.ENVIRONMENT}")
    print()

    test_email = input("Enter test email address (or press Enter to skip): ").strip()

    if not test_email:
        print("\nSkipping email tests (no email provided)")
        print("\nIn development mode, emails will be logged instead of sent.")
        return

    print(f"\nTesting with email: {test_email}")
    print()

    # Test 1: Magic Link Email
    print("1. Testing Magic Link Email...")
    try:
        result = await email_service.send_magic_link(
            to=test_email,
            token="test-token-123456",
            app_url=settings.APP_URL
        )
        print(f"   Result: {'✓ Success' if result else '✗ Failed'}")
    except Exception as e:
        print(f"   Result: ✗ Error - {str(e)}")
    print()

    # Test 2: Welcome Email
    print("2. Testing Welcome Email...")
    try:
        result = await email_service.send_welcome_email(
            to=test_email,
            name="Test User"
        )
        print(f"   Result: {'✓ Success' if result else '✗ Failed'}")
    except Exception as e:
        print(f"   Result: ✗ Error - {str(e)}")
    print()

    # Test 3: Action Notification Email
    print("3. Testing Action Notification Email...")
    try:
        result = await email_service.send_action_notification(
            to=test_email,
            action_summary="Delete email from John Doe with subject 'Important Meeting'",
            queue_url=f"{settings.APP_URL}/queue/test-action-id",
            action_type="HIGH_RISK"
        )
        print(f"   Result: {'✓ Success' if result else '✗ Failed'}")
    except Exception as e:
        print(f"   Result: ✗ Error - {str(e)}")
    print()

    # Test 4: Daily Digest Email
    print("4. Testing Daily Digest Email...")
    try:
        stats = {
            'emails_processed': 42,
            'responses_sent': 15,
            'time_saved_minutes': 120
        }
        pending_actions = [
            {'type': 'DELETE', 'summary': 'Delete spam email from unknown sender'},
            {'type': 'REPLY', 'summary': 'Send reply to meeting request'},
            {'type': 'FORWARD', 'summary': 'Forward document to team'}
        ]
        result = await email_service.send_daily_digest(
            to=test_email,
            stats=stats,
            pending_actions=pending_actions,
            date=datetime.utcnow()
        )
        print(f"   Result: {'✓ Success' if result else '✗ Failed'}")
    except Exception as e:
        print(f"   Result: ✗ Error - {str(e)}")
    print()

    print("=" * 60)
    print("Email Service Tests Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_email_service())
