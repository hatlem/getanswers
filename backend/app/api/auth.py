from datetime import datetime, timedelta
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import redis.asyncio as redis

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import get_redis
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
    generate_magic_link_token,
    verify_token,
    validate_password_strength,
    sanitize_email,
)
from app.core.exceptions import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    DatabaseError
)
from app.core.logging import logger
from app.core.audit import AuditLog
from app.core.utils import get_client_ip
from app.models import User, MagicLink, Organization, OrganizationMember, OrganizationRole
from app.api.deps import get_current_user
from app.services.email import email_service


def generate_unique_slug(name: str) -> str:
    """Generate a unique slug from a name."""
    import re
    import secrets
    # Convert to lowercase, replace spaces with hyphens, remove non-alphanumeric
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    # Add random suffix for uniqueness
    slug = f"{slug}-{secrets.token_hex(4)}"
    return slug[:100]  # Max 100 chars


async def create_personal_organization(
    db: AsyncSession,
    user: User
) -> Organization:
    """Create a personal organization for a user."""
    org = Organization(
        name=f"{user.name}'s Workspace",
        slug=generate_unique_slug(user.email.split('@')[0]),
        is_personal=True,
        is_active=True
    )
    db.add(org)
    await db.flush()

    # Add user as owner
    member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=OrganizationRole.OWNER,
        is_active=True,
        accepted_at=datetime.utcnow()
    )
    db.add(member)

    # Set as user's current organization
    user.current_organization_id = org.id

    return org

router = APIRouter()


# Rate limiting configuration
MAGIC_LINK_RATE_LIMIT = 3  # Max requests per hour
MAGIC_LINK_RATE_WINDOW = 3600  # 1 hour in seconds


async def check_magic_link_rate_limit(email: str, redis_client: redis.Redis) -> bool:
    """
    Check if email has exceeded magic link rate limit.

    Args:
        email: Email address to check
        redis_client: Redis client instance

    Returns:
        True if rate limit exceeded, False otherwise
    """
    key = f"magic_link_rate:{email}"

    try:
        # Get current count
        count = await redis_client.get(key)

        if count is None:
            # First request - set count to 1 with expiry
            await redis_client.setex(key, MAGIC_LINK_RATE_WINDOW, 1)
            return False

        count = int(count)

        if count >= MAGIC_LINK_RATE_LIMIT:
            # Rate limit exceeded
            return True

        # Increment count
        await redis_client.incr(key)
        return False

    except Exception as e:
        logger.error(f"Error checking rate limit for {email}: {str(e)}")
        # On error, deny the request (fail closed) for security
        # This prevents abuse if Redis is down or misconfigured
        return True


# Request/Response Schemas
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    name: str = Field(..., min_length=1, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class MagicLinkRequest(BaseModel):
    email: EmailStr


class VerifyMagicLinkRequest(BaseModel):
    token: str = Field(..., description="Magic link token from email")


class OrganizationInfo(BaseModel):
    id: UUID
    name: str
    slug: str
    is_personal: bool


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    is_super_admin: bool = False
    current_organization: Optional[OrganizationInfo] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse
    access_token: str


class MessageResponse(BaseModel):
    message: str


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    req: Request,
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user with email and password."""
    client_ip = get_client_ip(req)

    # Sanitize email
    email = sanitize_email(request.email)

    # Validate password strength
    valid, error_message = validate_password_strength(request.password)
    if not valid:
        await AuditLog.log_registration(
            email=email,
            ip_address=client_ip,
            success=False,
        )
        raise ValidationError(error_message)

    try:
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            # Don't reveal that email exists in audit log (security)
            await AuditLog.log_registration(
                email=email,
                ip_address=client_ip,
                success=False,
            )
            raise ConflictError("Email already registered")

        # Create new user
        new_user = User(
            email=email,
            name=request.name,
            password_hash=hash_password(request.password)
        )

        db.add(new_user)
        await db.flush()  # Get user ID before creating org

        # Create personal organization for the user
        await create_personal_organization(db, new_user)

        await db.commit()
        await db.refresh(new_user)

        # Log successful registration
        await AuditLog.log_registration(
            email=email,
            ip_address=client_ip,
            success=True,
            user_id=str(new_user.id),
        )
        logger.info(f"Created user {email} with personal organization")
    except ConflictError:
        raise
    except Exception as e:
        logger.error(f"Failed to register user {email}: {e}", exc_info=True)
        await AuditLog.log_registration(
            email=email,
            ip_address=client_ip,
            success=False,
        )
        raise DatabaseError("Failed to register user")

    # Send welcome email (non-blocking - don't fail registration if email fails)
    try:
        await email_service.send_welcome_email(new_user.email, new_user.name)
    except Exception as e:
        logger.error(f"Failed to send welcome email to {new_user.email}: {str(e)}")

    # Create access token
    access_token = create_access_token(data={"sub": str(new_user.id)})

    # Build response manually to avoid lazy loading issues
    current_org = None
    if new_user.current_organization_id:
        org_result = await db.execute(
            select(Organization).where(Organization.id == new_user.current_organization_id)
        )
        org = org_result.scalar_one_or_none()
        if org:
            current_org = OrganizationInfo(
                id=org.id,
                name=org.name,
                slug=org.slug,
                is_personal=org.is_personal
            )

    return AuthResponse(
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            name=new_user.name,
            is_super_admin=new_user.is_super_admin,
            current_organization=current_org,
            created_at=new_user.created_at
        ),
        access_token=access_token
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    req: Request,
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password."""
    client_ip = get_client_ip(req)
    email = sanitize_email(request.email)

    try:
        # Find user by email
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not user.password_hash:
            logger.warning(f"Failed login attempt for {email}: user not found or no password")
            await AuditLog.log_login_attempt(
                email=email,
                success=False,
                ip_address=client_ip,
                failure_reason="user_not_found",
            )
            raise AuthenticationError("Invalid email or password")

        # Verify password
        if not verify_password(request.password, user.password_hash):
            logger.warning(f"Failed login attempt for {email}: incorrect password")
            await AuditLog.log_login_attempt(
                email=email,
                success=False,
                ip_address=client_ip,
                user_id=str(user.id),
                failure_reason="invalid_password",
            )
            raise AuthenticationError("Invalid email or password")

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Log successful login
        await AuditLog.log_login_attempt(
            email=email,
            success=True,
            ip_address=client_ip,
            user_id=str(user.id),
        )

        # Build response manually to avoid lazy loading issues
        current_org = None
        if user.current_organization_id:
            org_result = await db.execute(
                select(Organization).where(Organization.id == user.current_organization_id)
            )
            org = org_result.scalar_one_or_none()
            if org:
                current_org = OrganizationInfo(
                    id=org.id,
                    name=org.name,
                    slug=org.slug,
                    is_personal=org.is_personal
                )

        logger.info(f"User {user.email} logged in successfully")
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                is_super_admin=user.is_super_admin,
                current_organization=current_org,
                created_at=user.created_at
            ),
            access_token=access_token
        )
    except AuthenticationError:
        raise
    except Exception as e:
        logger.error(f"Login error for {email}: {e}", exc_info=True)
        await AuditLog.log_login_attempt(
            email=email,
            success=False,
            ip_address=client_ip,
            failure_reason="database_error",
        )
        raise DatabaseError("Failed to process login")


@router.post("/magic-link", response_model=MessageResponse)
async def request_magic_link(
    req: Request,
    request: MagicLinkRequest,
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Request a magic link for passwordless authentication."""
    client_ip = get_client_ip(req)
    email = sanitize_email(request.email)

    # Check rate limit
    rate_limited = await check_magic_link_rate_limit(email, redis_client)
    if rate_limited:
        logger.warning(f"Magic link rate limit exceeded for {email}")
        await AuditLog.log_magic_link_request(
            email=email,
            ip_address=client_ip,
            success=False,
        )
        raise RateLimitError(retry_after=MAGIC_LINK_RATE_WINDOW)

    # Find or create user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    is_new_user = False
    if not user:
        # Create new user without password
        user = User(
            email=email,
            name=email.split("@")[0],
            password_hash=None
        )
        db.add(user)
        await db.flush()  # Get user ID before creating org

        # Create personal organization for the user
        await create_personal_organization(db, user)

        await db.commit()
        await db.refresh(user)
        is_new_user = True
        logger.info(f"Created user {email} with personal organization via magic link")

    # Generate magic link token
    token = generate_magic_link_token()

    # Save magic link to database
    magic_link = MagicLink(
        user_id=user.id,
        email=email,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.MAGIC_LINK_EXPIRE_MINUTES)
    )

    db.add(magic_link)
    await db.commit()

    # Send magic link email
    try:
        email_sent = await email_service.send_magic_link(
            to=email,
            token=token,
        )

        if not email_sent:
            logger.error(f"Failed to send magic link to {email}")
            await AuditLog.log_magic_link_request(
                email=email,
                ip_address=client_ip,
                success=False,
            )
            raise DatabaseError("Failed to send magic link email. Please try again.")

        # If new user, also send welcome email
        if is_new_user:
            try:
                await email_service.send_welcome_email(user.email, user.name)
            except Exception as e:
                logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
                # Don't fail the request if welcome email fails

    except DatabaseError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending magic link to {email}: {str(e)}", exc_info=True)
        await AuditLog.log_magic_link_request(
            email=email,
            ip_address=client_ip,
            success=False,
        )
        raise DatabaseError("Failed to send magic link email. Please try again.")

    # Log successful magic link request
    await AuditLog.log_magic_link_request(
        email=email,
        ip_address=client_ip,
        success=True,
    )

    logger.info(f"Magic link sent successfully to {email}")
    return MessageResponse(message="Check your email for the magic link")


@router.post("/verify", response_model=AuthResponse)
async def verify_magic_link(
    req: Request,
    request: VerifyMagicLinkRequest,
    db: AsyncSession = Depends(get_db)
):
    """Verify a magic link token and authenticate the user."""
    client_ip = get_client_ip(req)

    try:
        # Find magic link
        result = await db.execute(select(MagicLink).where(MagicLink.token == request.token))
        magic_link = result.scalar_one_or_none()

        if not magic_link:
            logger.warning(f"Invalid magic link token attempt from {client_ip}")
            await AuditLog.log_magic_link_verify(
                email="unknown",
                ip_address=client_ip,
                success=False,
                failure_reason="invalid_token",
            )
            raise ValidationError("Invalid magic link token")

        # Check if already used
        if magic_link.is_used:
            logger.warning(f"Attempted to use already-used magic link for {magic_link.email}")
            await AuditLog.log_magic_link_verify(
                email=magic_link.email,
                ip_address=client_ip,
                success=False,
                failure_reason="already_used",
            )
            raise ValidationError("Magic link has already been used")

        # Check if expired
        if magic_link.is_expired:
            logger.warning(f"Attempted to use expired magic link for {magic_link.email}")
            await AuditLog.log_magic_link_verify(
                email=magic_link.email,
                ip_address=client_ip,
                success=False,
                failure_reason="expired",
            )
            raise ValidationError("Magic link has expired")

        # Mark as used
        magic_link.used_at = datetime.utcnow()
        await db.commit()

        # Get user
        user_result = await db.execute(select(User).where(User.id == magic_link.user_id))
        user = user_result.scalar_one_or_none()

        if not user:
            logger.error(f"User not found for magic link: {magic_link.user_id}")
            await AuditLog.log_magic_link_verify(
                email=magic_link.email,
                ip_address=client_ip,
                success=False,
                failure_reason="user_not_found",
            )
            raise NotFoundError("User", str(magic_link.user_id))

        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})

        # Log successful verification
        await AuditLog.log_magic_link_verify(
            email=user.email,
            ip_address=client_ip,
            success=True,
            user_id=str(user.id),
        )

        # Build response manually to avoid lazy loading issues
        current_org = None
        if user.current_organization_id:
            org_result = await db.execute(
                select(Organization).where(Organization.id == user.current_organization_id)
            )
            org = org_result.scalar_one_or_none()
            if org:
                current_org = OrganizationInfo(
                    id=org.id,
                    name=org.name,
                    slug=org.slug,
                    is_personal=org.is_personal
                )

        logger.info(f"User {user.email} authenticated via magic link")
        return AuthResponse(
            user=UserResponse(
                id=user.id,
                email=user.email,
                name=user.name,
                is_super_admin=user.is_super_admin,
                current_organization=current_org,
                created_at=user.created_at
            ),
            access_token=access_token
        )
    except (ValidationError, NotFoundError):
        raise
    except Exception as e:
        logger.error(f"Error verifying magic link: {e}", exc_info=True)
        raise DatabaseError("Failed to verify magic link")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the current authenticated user's information."""
    # Load current organization if set
    current_org = None
    if current_user.current_organization_id:
        from sqlalchemy.orm import selectinload
        org_result = await db.execute(
            select(Organization).where(Organization.id == current_user.current_organization_id)
        )
        org = org_result.scalar_one_or_none()
        if org:
            current_org = OrganizationInfo(
                id=org.id,
                name=org.name,
                slug=org.slug,
                is_personal=org.is_personal
            )

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        is_super_admin=current_user.is_super_admin,
        current_organization=current_org,
        created_at=current_user.created_at
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh the access token for the current user.
    This endpoint allows users to get a new access token before their current one expires.
    """
    # Create a new access token
    access_token = create_access_token(data={"sub": str(current_user.id)})

    # Build response manually to avoid lazy loading issues
    current_org = None
    if current_user.current_organization_id:
        org_result = await db.execute(
            select(Organization).where(Organization.id == current_user.current_organization_id)
        )
        org = org_result.scalar_one_or_none()
        if org:
            current_org = OrganizationInfo(
                id=org.id,
                name=org.name,
                slug=org.slug,
                is_personal=org.is_personal
            )

    return AuthResponse(
        user=UserResponse(
            id=current_user.id,
            email=current_user.email,
            name=current_user.name,
            is_super_admin=current_user.is_super_admin,
            current_organization=current_org,
            created_at=current_user.created_at
        ),
        access_token=access_token
    )


@router.post("/logout", response_model=MessageResponse)
async def logout():
    """Logout the current user (client-side token deletion)."""
    return MessageResponse(message="Logged out successfully")
