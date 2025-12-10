"""
Email service for transactional emails using GetMailer.

GetMailer is our internal email solution built on AWS SES.
Used for: magic links, welcome emails, notifications, digests.

NOT for user emails - those go through Gmail/Outlook OAuth.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Transactional email service using GetMailer.

    Usage:
        email_service = EmailService()
        await email_service.send_magic_link("user@example.com", "token123")

    Configuration (in .env):
        GETMAILER_API_KEY=gm_xxxxx
        GETMAILER_URL=https://api.getmailer.io  # optional, has default
        EMAIL_FROM=noreply@getanswers.co
    """

    def __init__(self):
        self.api_key = settings.GETMAILER_API_KEY
        self.base_url = settings.GETMAILER_URL
        self.from_email = settings.EMAIL_FROM
        self.app_url = settings.APP_URL

        if not self.api_key:
            logger.warning(
                "GETMAILER_API_KEY not configured. Emails will be logged but not sent."
            )

    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """
        Send an email via GetMailer.

        Returns True if sent successfully, False otherwise.
        """
        try:
            if not self.api_key:
                # Development fallback - just log
                logger.info(f"[EMAIL] To: {to}, Subject: {subject}")
                if settings.is_development:
                    logger.debug(f"[EMAIL BODY]\n{text_body or html_body[:500]}")
                return True

            async with httpx.AsyncClient() as client:
                payload = {
                    "from": self.from_email,
                    "to": to,
                    "subject": subject,
                    "html": html_body,
                }

                if text_body:
                    payload["text"] = text_body
                if tags:
                    payload["tags"] = tags

                response = await client.post(
                    f"{self.base_url}/v1/emails/send",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                    timeout=30.0,
                )

                if response.status_code >= 400:
                    logger.error(f"GetMailer API error: {response.status_code} - {response.text}")
                    return False

                data = response.json()
                logger.info(f"Email sent to {to}, message_id: {data.get('id')}")
                return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {e}")
            return False

    async def send_magic_link(self, to: str, token: str) -> bool:
        """Send magic link authentication email."""
        magic_link_url = f"{self.app_url}/auth/verify?token={token}"

        subject = "Sign in to GetAnswers"
        html_body = self._get_magic_link_template(magic_link_url, to)
        text_body = f"""
Sign in to GetAnswers

Click the link below to sign in to your account:
{magic_link_url}

This link will expire in 15 minutes.

If you didn't request this email, you can safely ignore it.

---
GetAnswers - AI-powered email management
        """.strip()

        return await self.send_email(to, subject, html_body, text_body, tags=["auth", "magic-link"])

    async def send_welcome_email(self, to: str, name: str) -> bool:
        """Send welcome email after registration."""
        subject = f"Welcome to GetAnswers, {name}!"
        html_body = self._get_welcome_template(name)
        text_body = f"""
Welcome to GetAnswers, {name}!

Thank you for joining GetAnswers - your AI-powered email management assistant.

GetAnswers helps you:
- Automatically categorize and prioritize emails
- Draft intelligent responses using Claude AI
- Manage high-risk actions with human-in-the-loop
- Get daily summaries of AI activity

Get started: {self.app_url}/dashboard

---
GetAnswers Team
        """.strip()

        return await self.send_email(to, subject, html_body, text_body, tags=["onboarding", "welcome"])

    async def send_action_notification(
        self,
        to: str,
        action_summary: str,
        action_id: str,
        risk_level: str = "HIGH",
    ) -> bool:
        """Notify user of pending high-risk action."""
        queue_url = f"{self.app_url}/queue?action={action_id}"
        subject = f"[{risk_level}] Action Required: Approve pending email"

        html_body = self._get_action_notification_template(action_summary, queue_url, risk_level)
        text_body = f"""
Action Required: Approve pending email action

Risk Level: {risk_level}

Your AI assistant needs approval for:
{action_summary}

Review and approve: {queue_url}

---
GetAnswers
        """.strip()

        return await self.send_email(to, subject, html_body, text_body, tags=["notification", "action-required"])

    async def send_daily_digest(
        self,
        to: str,
        stats: Dict[str, Any],
        pending_actions: List[Dict],
        date: Optional[datetime] = None,
    ) -> bool:
        """Send daily summary of AI activity."""
        digest_date = date or datetime.utcnow()
        subject = f"GetAnswers Daily Digest - {digest_date.strftime('%B %d, %Y')}"

        html_body = self._get_daily_digest_template(stats, pending_actions, digest_date)
        text_body = f"""
Daily Digest - {digest_date.strftime('%B %d, %Y')}

Activity Summary:
- Emails processed: {stats.get('emails_processed', 0)}
- Responses sent: {stats.get('responses_sent', 0)}
- Actions pending: {len(pending_actions)}
- Time saved: ~{stats.get('time_saved_minutes', 0)} minutes

View dashboard: {self.app_url}/dashboard

---
GetAnswers
        """.strip()

        return await self.send_email(to, subject, html_body, text_body, tags=["digest", "daily"])

    # =========================================================================
    # HTML Email Templates
    # =========================================================================

    def _base_template(self, content: str) -> str:
        """Wrap content in base email template."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f5f5;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    {content}
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 24px 40px; border-top: 1px solid #eeeeee; text-align: center;">
                            <p style="margin: 0; font-size: 12px; color: #999999;">
                                GetAnswers - AI-powered email management
                            </p>
                            <p style="margin: 8px 0 0; font-size: 11px; color: #cccccc;">
                                <a href="{self.app_url}/unsubscribe" style="color: #999999;">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """.strip()

    def _get_magic_link_template(self, magic_link_url: str, email: str) -> str:
        content = f"""
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center;">
                            <h1 style="margin: 0; font-size: 28px; font-weight: 600; color: #1a1a1a;">
                                GetAnswers
                            </h1>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <h2 style="margin: 0 0 16px; font-size: 20px; font-weight: 500; color: #333333;">
                                Sign in to your account
                            </h2>
                            <p style="margin: 0 0 24px; font-size: 16px; line-height: 1.5; color: #666666;">
                                Click the button below to securely sign in. This link expires in 15 minutes.
                            </p>
                        </td>
                    </tr>
                    <!-- CTA Button -->
                    <tr>
                        <td style="padding: 0 40px 40px; text-align: center;">
                            <a href="{magic_link_url}" style="display: inline-block; padding: 14px 32px; background-color: #2563eb; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 500;">
                                Sign in to GetAnswers
                            </a>
                        </td>
                    </tr>
                    <!-- Info -->
                    <tr>
                        <td style="padding: 0 40px 40px;">
                            <p style="margin: 0; font-size: 14px; color: #999999;">
                                Signing in as: <strong style="color: #666666;">{email}</strong>
                            </p>
                        </td>
                    </tr>
        """
        return self._base_template(content)

    def _get_welcome_template(self, name: str) -> str:
        content = f"""
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px; text-align: center;">
                            <h1 style="margin: 0; font-size: 28px; font-weight: 600; color: #1a1a1a;">
                                Welcome to GetAnswers!
                            </h1>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <p style="margin: 0 0 24px; font-size: 16px; line-height: 1.6; color: #333333;">
                                Hi {name},
                            </p>
                            <p style="margin: 0 0 24px; font-size: 16px; line-height: 1.6; color: #666666;">
                                Thank you for joining GetAnswers! We're excited to help you manage your emails more efficiently.
                            </p>
                            <h3 style="margin: 0 0 16px; font-size: 18px; font-weight: 600; color: #333333;">
                                What GetAnswers can do:
                            </h3>
                            <ul style="margin: 0 0 24px; padding-left: 20px; color: #666666; line-height: 1.8;">
                                <li>Automatically categorize and prioritize emails</li>
                                <li>Draft intelligent responses using AI</li>
                                <li>Human-in-the-loop for high-risk actions</li>
                                <li>Daily summaries of AI activity</li>
                            </ul>
                        </td>
                    </tr>
                    <!-- CTA Button -->
                    <tr>
                        <td style="padding: 0 40px 40px; text-align: center;">
                            <a href="{self.app_url}/dashboard" style="display: inline-block; padding: 14px 32px; background-color: #2563eb; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 500;">
                                Go to Dashboard
                            </a>
                        </td>
                    </tr>
        """
        return self._base_template(content)

    def _get_action_notification_template(self, summary: str, queue_url: str, risk: str) -> str:
        risk_colors = {
            "HIGH": ("#dc2626", "#fef2f2"),
            "MEDIUM": ("#f59e0b", "#fffbeb"),
            "LOW": ("#2563eb", "#eff6ff"),
        }
        badge_color, bg_color = risk_colors.get(risk, risk_colors["HIGH"])

        content = f"""
                    <!-- Header with Risk Badge -->
                    <tr>
                        <td style="padding: 40px 40px 20px;">
                            <table role="presentation" style="width: 100%;">
                                <tr>
                                    <td>
                                        <h1 style="margin: 0; font-size: 24px; font-weight: 600; color: #1a1a1a;">
                                            Action Required
                                        </h1>
                                    </td>
                                    <td style="text-align: right;">
                                        <span style="display: inline-block; padding: 4px 12px; background-color: {badge_color}; color: #ffffff; border-radius: 4px; font-size: 12px; font-weight: 600;">
                                            {risk} RISK
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Content -->
                    <tr>
                        <td style="padding: 20px 40px;">
                            <p style="margin: 0 0 16px; font-size: 16px; color: #333333;">
                                Your AI assistant needs approval for:
                            </p>
                            <div style="padding: 16px; background-color: {bg_color}; border-left: 3px solid {badge_color}; border-radius: 4px;">
                                <p style="margin: 0; font-size: 15px; line-height: 1.5; color: #333333;">
                                    {summary}
                                </p>
                            </div>
                        </td>
                    </tr>
                    <!-- CTA Button -->
                    <tr>
                        <td style="padding: 20px 40px 40px; text-align: center;">
                            <a href="{queue_url}" style="display: inline-block; padding: 14px 32px; background-color: #2563eb; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 500;">
                                Review and Approve
                            </a>
                        </td>
                    </tr>
        """
        return self._base_template(content)

    def _get_daily_digest_template(self, stats: Dict, pending: List, date: datetime) -> str:
        pending_rows = ""
        for action in pending[:5]:
            pending_rows += f"""
                <tr>
                    <td style="padding: 12px; border-bottom: 1px solid #eeeeee; font-size: 14px; color: #333333;">
                        {action.get('summary', 'Action pending')}
                    </td>
                </tr>
            """
        if len(pending) > 5:
            pending_rows += f"""
                <tr>
                    <td style="padding: 12px; text-align: center; font-size: 14px; color: #666666;">
                        ...and {len(pending) - 5} more
                    </td>
                </tr>
            """
        if not pending:
            pending_rows = """
                <tr>
                    <td style="padding: 12px; text-align: center; font-size: 14px; color: #999999;">
                        No pending actions - you're all caught up!
                    </td>
                </tr>
            """

        content = f"""
                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px;">
                            <h1 style="margin: 0; font-size: 24px; font-weight: 600; color: #1a1a1a;">
                                Daily Digest
                            </h1>
                            <p style="margin: 8px 0 0; font-size: 14px; color: #999999;">
                                {date.strftime('%B %d, %Y')}
                            </p>
                        </td>
                    </tr>
                    <!-- Stats -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <table role="presentation" style="width: 100%;">
                                <tr>
                                    <td style="width: 33%; padding: 16px; background-color: #eff6ff; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 28px; font-weight: 700; color: #2563eb;">
                                            {stats.get('emails_processed', 0)}
                                        </div>
                                        <div style="font-size: 11px; color: #666666; text-transform: uppercase;">
                                            Processed
                                        </div>
                                    </td>
                                    <td style="width: 2%;"></td>
                                    <td style="width: 33%; padding: 16px; background-color: #f0fdf4; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 28px; font-weight: 700; color: #16a34a;">
                                            {stats.get('responses_sent', 0)}
                                        </div>
                                        <div style="font-size: 11px; color: #666666; text-transform: uppercase;">
                                            Sent
                                        </div>
                                    </td>
                                    <td style="width: 2%;"></td>
                                    <td style="width: 33%; padding: 16px; background-color: #fef3c7; border-radius: 6px; text-align: center;">
                                        <div style="font-size: 28px; font-weight: 700; color: #ca8a04;">
                                            {stats.get('time_saved_minutes', 0)}
                                        </div>
                                        <div style="font-size: 11px; color: #666666; text-transform: uppercase;">
                                            Min Saved
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Pending Actions -->
                    <tr>
                        <td style="padding: 20px 40px 0;">
                            <h2 style="margin: 0 0 16px; font-size: 18px; font-weight: 600; color: #333333;">
                                Pending Actions ({len(pending)})
                            </h2>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <table role="presentation" style="width: 100%; border: 1px solid #eeeeee; border-radius: 6px;">
                                {pending_rows}
                            </table>
                        </td>
                    </tr>
                    <!-- CTA Button -->
                    <tr>
                        <td style="padding: 20px 40px 40px; text-align: center;">
                            <a href="{self.app_url}/dashboard" style="display: inline-block; padding: 14px 32px; background-color: #2563eb; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 500;">
                                View Dashboard
                            </a>
                        </td>
                    </tr>
        """
        return self._base_template(content)


# Global email service instance
email_service = EmailService()
