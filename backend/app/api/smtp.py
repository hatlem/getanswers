"""SMTP/IMAP email connection API endpoints.

This module provides endpoints for:
- Testing and storing SMTP/IMAP credentials
- Disconnecting SMTP email
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/smtp", tags=["SMTP Email"])


# Request/Response Schemas
class SMTPCredentials(BaseModel):
    """SMTP/IMAP credentials for email connection."""
    email: EmailStr = Field(description="Email address")
    password: str = Field(description="Email password or app-specific password")
    imap_server: str = Field(description="IMAP server hostname (e.g., imap.gmail.com)")
    imap_port: int = Field(default=993, description="IMAP port (usually 993 for SSL)")
    smtp_server: str = Field(description="SMTP server hostname (e.g., smtp.gmail.com)")
    smtp_port: int = Field(default=587, description="SMTP port (usually 587 for TLS)")
    use_ssl: bool = Field(default=True, description="Use SSL/TLS for connections")


class SMTPConnectionStatus(BaseModel):
    """SMTP connection status response."""
    connected: bool = Field(description="Whether SMTP is connected")
    email: Optional[str] = Field(None, description="Connected email address")
    imap_server: Optional[str] = Field(None, description="IMAP server")
    smtp_server: Optional[str] = Field(None, description="SMTP server")
    connected_at: Optional[str] = Field(None, description="When the connection was established")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class TestConnectionResponse(BaseModel):
    """Connection test result."""
    success: bool
    imap_status: str
    smtp_status: str
    message: str


async def test_imap_connection(credentials: SMTPCredentials) -> tuple[bool, str]:
    """Test IMAP connection with provided credentials.

    Returns:
        Tuple of (success, message)
    """
    import imaplib
    import ssl

    try:
        if credentials.use_ssl:
            context = ssl.create_default_context()
            mail = imaplib.IMAP4_SSL(
                credentials.imap_server,
                credentials.imap_port,
                ssl_context=context
            )
        else:
            mail = imaplib.IMAP4(credentials.imap_server, credentials.imap_port)

        mail.login(credentials.email, credentials.password)
        mail.logout()
        return True, "IMAP connection successful"
    except imaplib.IMAP4.error as e:
        return False, f"IMAP authentication failed: {str(e)}"
    except Exception as e:
        return False, f"IMAP connection failed: {str(e)}"


async def test_smtp_connection(credentials: SMTPCredentials) -> tuple[bool, str]:
    """Test SMTP connection with provided credentials.

    Returns:
        Tuple of (success, message)
    """
    import smtplib
    import ssl

    try:
        if credentials.smtp_port == 465:
            # SSL from the start
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL(
                credentials.smtp_server,
                credentials.smtp_port,
                context=context
            )
        else:
            # STARTTLS
            server = smtplib.SMTP(credentials.smtp_server, credentials.smtp_port)
            server.starttls()

        server.login(credentials.email, credentials.password)
        server.quit()
        return True, "SMTP connection successful"
    except smtplib.SMTPAuthenticationError as e:
        return False, f"SMTP authentication failed: {str(e)}"
    except Exception as e:
        return False, f"SMTP connection failed: {str(e)}"


@router.post("/test", response_model=TestConnectionResponse)
async def test_smtp_credentials(
    credentials: SMTPCredentials,
    current_user: User = Depends(get_current_user)
):
    """Test SMTP/IMAP credentials without saving them.

    This endpoint tests the provided credentials against the IMAP and SMTP servers
    to verify they work before saving them.

    Args:
        credentials: SMTP/IMAP credentials to test
        current_user: Authenticated user from JWT token

    Returns:
        Test results for both IMAP and SMTP connections
    """
    logger.info(f"Testing SMTP credentials for user {current_user.id}")

    # Test both connections
    imap_success, imap_message = await test_imap_connection(credentials)
    smtp_success, smtp_message = await test_smtp_connection(credentials)

    overall_success = imap_success and smtp_success

    if overall_success:
        message = "All connections successful! Credentials are valid."
    elif imap_success:
        message = "IMAP works but SMTP failed. Check SMTP settings."
    elif smtp_success:
        message = "SMTP works but IMAP failed. Check IMAP settings."
    else:
        message = "Both connections failed. Please verify your credentials and server settings."

    return TestConnectionResponse(
        success=overall_success,
        imap_status=imap_message,
        smtp_status=smtp_message,
        message=message
    )


@router.post("", response_model=SMTPConnectionStatus)
async def connect_smtp(
    credentials: SMTPCredentials,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect email using SMTP/IMAP credentials.

    This endpoint tests the credentials and if successful, stores them
    securely in the user's profile.

    Args:
        credentials: SMTP/IMAP credentials to save
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        Connection status
    """
    logger.info(f"Connecting SMTP for user {current_user.id}")

    # Test credentials first
    imap_success, imap_message = await test_imap_connection(credentials)
    if not imap_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"IMAP connection failed: {imap_message}"
        )

    smtp_success, smtp_message = await test_smtp_connection(credentials)
    if not smtp_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SMTP connection failed: {smtp_message}"
        )

    # Store credentials (password should be encrypted in production)
    # For now, we store it as-is but in production, use proper encryption
    smtp_creds = {
        "email": credentials.email,
        "password": credentials.password,  # TODO: Encrypt this
        "imap_server": credentials.imap_server,
        "imap_port": credentials.imap_port,
        "smtp_server": credentials.smtp_server,
        "smtp_port": credentials.smtp_port,
        "use_ssl": credentials.use_ssl,
    }

    current_user.smtp_credentials = smtp_creds
    current_user.email_provider = 'smtp'
    await db.commit()
    await db.refresh(current_user)

    logger.info(f"Successfully connected SMTP for user {current_user.id}")

    return SMTPConnectionStatus(
        connected=True,
        email=credentials.email,
        imap_server=credentials.imap_server,
        smtp_server=credentials.smtp_server,
        connected_at=current_user.updated_at.isoformat() if current_user.updated_at else None
    )


@router.delete("", response_model=MessageResponse)
async def disconnect_smtp(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Disconnect SMTP/IMAP email integration.

    This endpoint removes the stored credentials from the user's profile.

    Args:
        current_user: Authenticated user from JWT token
        db: Database session

    Returns:
        Success message
    """
    if not current_user.smtp_credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SMTP is not connected"
        )

    current_user.smtp_credentials = None
    if current_user.email_provider == 'smtp':
        current_user.email_provider = None
    await db.commit()

    logger.info(f"Disconnected SMTP for user {current_user.id}")

    return MessageResponse(message="SMTP email disconnected successfully")


@router.get("/status", response_model=SMTPConnectionStatus)
async def get_smtp_status(
    current_user: User = Depends(get_current_user)
):
    """Get SMTP connection status.

    Check if the user has SMTP/IMAP credentials configured.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        Connection status with server info if connected
    """
    if not current_user.smtp_credentials:
        return SMTPConnectionStatus(
            connected=False,
            email=None,
            imap_server=None,
            smtp_server=None,
            connected_at=None
        )

    creds = current_user.smtp_credentials
    return SMTPConnectionStatus(
        connected=True,
        email=creds.get("email"),
        imap_server=creds.get("imap_server"),
        smtp_server=creds.get("smtp_server"),
        connected_at=current_user.updated_at.isoformat() if current_user.updated_at else None
    )


# Common SMTP/IMAP presets for popular providers
EMAIL_PRESETS = {
    "gmail": {
        "imap_server": "imap.gmail.com",
        "imap_port": 993,
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587,
        "use_ssl": True,
        "note": "Use an App Password from Google Account settings"
    },
    "outlook_hotmail": {
        "imap_server": "outlook.office365.com",
        "imap_port": 993,
        "smtp_server": "smtp.office365.com",
        "smtp_port": 587,
        "use_ssl": True,
        "note": "May require app password if 2FA is enabled"
    },
    "yahoo": {
        "imap_server": "imap.mail.yahoo.com",
        "imap_port": 993,
        "smtp_server": "smtp.mail.yahoo.com",
        "smtp_port": 587,
        "use_ssl": True,
        "note": "Generate an app password in Yahoo Account Security"
    },
    "icloud": {
        "imap_server": "imap.mail.me.com",
        "imap_port": 993,
        "smtp_server": "smtp.mail.me.com",
        "smtp_port": 587,
        "use_ssl": True,
        "note": "Generate an app-specific password in Apple ID settings"
    },
    "zoho": {
        "imap_server": "imap.zoho.com",
        "imap_port": 993,
        "smtp_server": "smtp.zoho.com",
        "smtp_port": 587,
        "use_ssl": True,
        "note": "Use your Zoho email credentials"
    },
    "protonmail": {
        "imap_server": "127.0.0.1",
        "imap_port": 1143,
        "smtp_server": "127.0.0.1",
        "smtp_port": 1025,
        "use_ssl": False,
        "note": "Requires ProtonMail Bridge application"
    }
}


@router.get("/presets")
async def get_email_presets():
    """Get preset SMTP/IMAP configurations for popular email providers.

    Returns:
        Dictionary of email provider presets
    """
    return EMAIL_PRESETS
