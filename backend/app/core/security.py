"""Security utilities for authentication and authorization."""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary of claims to include in the token
        expires_delta: Optional custom expiration time

    Returns:
        str: Encoded JWT token

    Example:
        token = create_access_token({"sub": user.email, "user_id": user.id})
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string to verify

    Returns:
        dict: Decoded token payload if valid

    Raises:
        ValueError: If token is invalid, expired, or malformed

    Example:
        try:
            payload = verify_token(token)
            user_id = payload.get("sub")
        except ValueError as e:
            # Handle invalid token
            pass
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.JWTClaimsError:
        raise ValueError("Invalid token claims")
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        str: Hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        bool: True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def generate_magic_link_token() -> str:
    """
    Generate a cryptographically secure token for magic links.

    Returns:
        str: URL-safe random token (32 bytes = 43 characters base64)

    Example:
        token = generate_magic_link_token()
        # Store token with expiration and send via email
    """
    return secrets.token_urlsafe(32)


def create_magic_link_token(email: str) -> str:
    """
    Create a JWT token specifically for magic link authentication.

    Args:
        email: User email address

    Returns:
        str: JWT token with short expiration for magic link

    Example:
        token = create_magic_link_token(user.email)
        magic_link = f"{settings.APP_URL}/auth/verify?token={token}"
    """
    expires_delta = timedelta(minutes=settings.MAGIC_LINK_EXPIRE_MINUTES)

    data = {
        "sub": email,
        "type": "magic_link",
    }

    return create_access_token(data, expires_delta=expires_delta)


def verify_magic_link_token(token: str) -> Optional[str]:
    """
    Verify a magic link token and extract the email.

    Args:
        token: Magic link JWT token

    Returns:
        str: Email address if token is valid, None otherwise

    Example:
        email = verify_magic_link_token(token)
        if email:
            # Create session for user
    """
    try:
        payload = verify_token(token)
    except ValueError:
        return None

    # Verify it's a magic link token
    if payload.get("type") != "magic_link":
        return None

    email = payload.get("sub")
    return email


def create_password_reset_token(email: str) -> str:
    """
    Create a JWT token for password reset.

    Args:
        email: User email address

    Returns:
        str: JWT token with short expiration for password reset

    Example:
        token = create_password_reset_token(user.email)
    """
    expires_delta = timedelta(minutes=settings.MAGIC_LINK_EXPIRE_MINUTES)

    data = {
        "sub": email,
        "type": "password_reset",
    }

    return create_access_token(data, expires_delta=expires_delta)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify a password reset token and extract the email.

    Args:
        token: Password reset JWT token

    Returns:
        str: Email address if token is valid, None otherwise
    """
    try:
        payload = verify_token(token)
    except ValueError:
        return None

    # Verify it's a password reset token
    if payload.get("type") != "password_reset":
        return None

    email = payload.get("sub")
    return email


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength against security requirements.

    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (optional but recommended)

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, "")
        If invalid: (False, "description of requirements")

    Example:
        valid, message = validate_password_strength("MyPass123!")
        if not valid:
            raise ValueError(message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"

    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"

    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one number"

    # Optional: Check for special characters (recommended but not required)
    # special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    # if not any(c in special_chars for c in password):
    #     return False, "Password should contain at least one special character"

    return True, ""


def sanitize_email(email: str) -> str:
    """
    Sanitize and normalize email address.

    Args:
        email: Email address to sanitize

    Returns:
        Normalized email address (lowercase, stripped)

    Example:
        email = sanitize_email("  User@EXAMPLE.com  ")
        # Returns: "user@example.com"
    """
    return email.strip().lower()
