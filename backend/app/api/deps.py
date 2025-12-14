from typing import Optional
from uuid import UUID
from fastapi import Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_token
from app.core.exceptions import AuthenticationError, AuthorizationError, NotFoundError
from app.core.logging import logger
from app.models import User, Organization, OrganizationMember, OrganizationRole

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user.
    Validates JWT token from Authorization header and returns the user.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        User object for the authenticated user

    Raises:
        AuthenticationError: If token is invalid, expired, or user not found
    """
    token = credentials.credentials

    try:
        payload = verify_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise AuthenticationError("Invalid authentication credentials")
    except ValueError as e:
        logger.warning(f"Token verification failed: {e}")
        raise AuthenticationError(str(e))

    # Query user from database
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    except Exception as e:
        logger.error(f"Database error while fetching user: {e}", exc_info=True)
        raise AuthenticationError("Failed to authenticate user")

    if user is None:
        logger.warning(f"User not found for ID: {user_id}")
        raise AuthenticationError("User not found")

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Optional dependency to get the current authenticated user.
    Returns None if no valid authentication is provided instead of raising an error.

    Args:
        credentials: Optional HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if credentials is None:
        return None

    token = credentials.credentials

    try:
        payload = verify_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            return None

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user
    except (ValueError, Exception):
        return None


# =============================================================================
# Super Admin Dependencies
# =============================================================================

async def require_super_admin(
    user: User = Depends(get_current_user)
) -> User:
    """
    Dependency that requires the current user to be a super admin.
    Super admins have platform-wide administrative privileges.

    Args:
        user: Current authenticated user

    Returns:
        User object if user is a super admin

    Raises:
        AuthorizationError: If user is not a super admin
    """
    if not user.is_super_admin:
        logger.warning(f"Non-super-admin user {user.id} attempted super admin action")
        raise AuthorizationError("Super admin access required")
    return user


# =============================================================================
# Organization Context Dependencies
# =============================================================================

async def get_current_organization(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID")
) -> Organization:
    """
    Get the current organization context for the user.

    Priority:
    1. X-Organization-ID header (if provided and user is member)
    2. User's current_organization_id
    3. User's first organization membership (fallback)

    Args:
        user: Current authenticated user
        db: Database session
        x_organization_id: Optional organization ID from header

    Returns:
        Organization object for the current context

    Raises:
        AuthorizationError: If user has no organization or is not a member
    """
    org_id = None

    # Priority 1: Header
    if x_organization_id:
        try:
            org_id = UUID(x_organization_id)
        except ValueError:
            raise AuthorizationError("Invalid organization ID format")

    # Priority 2: User's current organization
    if not org_id and user.current_organization_id:
        org_id = user.current_organization_id

    # Verify membership if we have an org_id
    if org_id:
        result = await db.execute(
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.organization))
            .where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user.id,
                OrganizationMember.is_active == True
            )
        )
        member = result.scalar_one_or_none()

        if member:
            return member.organization

        # Super admins can access any organization
        if user.is_super_admin:
            org_result = await db.execute(
                select(Organization).where(Organization.id == org_id)
            )
            org = org_result.scalar_one_or_none()
            if org:
                return org

        raise AuthorizationError("Not a member of this organization")

    # Priority 3: First membership fallback
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.organization))
        .where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.is_active == True
        )
        .order_by(OrganizationMember.created_at)
        .limit(1)
    )
    member = result.scalar_one_or_none()

    if member:
        return member.organization

    raise AuthorizationError("No organization membership found")


async def get_current_organization_optional(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_organization_id: Optional[str] = Header(None, alias="X-Organization-ID")
) -> Optional[Organization]:
    """
    Optional version of get_current_organization.
    Returns None instead of raising an error if no organization context is found.
    """
    try:
        return await get_current_organization(user, db, x_organization_id)
    except AuthorizationError:
        return None


# =============================================================================
# Organization Role Dependencies
# =============================================================================

async def get_org_membership(
    organization: Organization = Depends(get_current_organization),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> OrganizationMember:
    """
    Get the current user's membership in the current organization.

    Args:
        organization: Current organization context
        user: Current authenticated user
        db: Database session

    Returns:
        OrganizationMember object

    Raises:
        AuthorizationError: If user is not a member
    """
    # Super admins get a virtual owner membership
    if user.is_super_admin:
        # Check if they have an actual membership
        result = await db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization.id,
                OrganizationMember.user_id == user.id,
                OrganizationMember.is_active == True
            )
        )
        member = result.scalar_one_or_none()
        if member:
            return member

        # Create a virtual membership for super admins
        virtual_member = OrganizationMember(
            organization_id=organization.id,
            user_id=user.id,
            role=OrganizationRole.OWNER,
            is_active=True
        )
        return virtual_member

    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == organization.id,
            OrganizationMember.user_id == user.id,
            OrganizationMember.is_active == True
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise AuthorizationError("Not a member of this organization")

    return member


def require_org_role(*allowed_roles: OrganizationRole):
    """
    Factory function that creates a dependency requiring specific organization roles.

    Args:
        allowed_roles: Roles that are allowed to perform the action

    Returns:
        Dependency function that validates role

    Usage:
        @router.post("/settings")
        async def update_settings(
            member: OrganizationMember = Depends(require_org_role(OrganizationRole.ADMIN, OrganizationRole.OWNER))
        ):
            ...
    """
    async def check_role(
        member: OrganizationMember = Depends(get_org_membership)
    ) -> OrganizationMember:
        if member.role not in allowed_roles:
            raise AuthorizationError(
                f"This action requires one of these roles: {', '.join(r.value for r in allowed_roles)}"
            )
        return member

    return check_role


async def require_org_owner(
    member: OrganizationMember = Depends(get_org_membership)
) -> OrganizationMember:
    """Require the current user to be an organization owner."""
    if member.role != OrganizationRole.OWNER:
        raise AuthorizationError("Organization owner access required")
    return member


async def require_org_admin(
    member: OrganizationMember = Depends(get_org_membership)
) -> OrganizationMember:
    """Require the current user to be at least an organization admin."""
    if member.role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN]:
        raise AuthorizationError("Organization admin access required")
    return member


async def require_org_manager(
    member: OrganizationMember = Depends(get_org_membership)
) -> OrganizationMember:
    """Require the current user to be at least an organization manager."""
    if member.role not in [OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.MANAGER]:
        raise AuthorizationError("Organization manager access required")
    return member


# =============================================================================
# Permission Check Dependencies
# =============================================================================

def require_permission(permission: str):
    """
    Factory function that creates a dependency requiring a specific permission.

    Args:
        permission: Permission name to check

    Returns:
        Dependency function that validates permission

    Usage:
        @router.post("/invite")
        async def invite_user(
            member: OrganizationMember = Depends(require_permission("manage_members"))
        ):
            ...
    """
    async def check_permission(
        member: OrganizationMember = Depends(get_org_membership)
    ) -> OrganizationMember:
        if not member.has_permission(permission):
            raise AuthorizationError(f"Permission required: {permission}")
        return member

    return check_permission
