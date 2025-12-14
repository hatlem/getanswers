"""Admin API endpoints for platform management (super admin only)."""
from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.core.logging import logger
from app.api.deps import require_super_admin
from app.models import (
    User, Organization, OrganizationMember, OrganizationInvite,
    OrganizationRole, Subscription, PlanTier, SubscriptionStatus
)

router = APIRouter()


def get_role_value(role: Union[OrganizationRole, str]) -> str:
    """Extract the string value from a role (handles both enum and string)."""
    return role.value if hasattr(role, 'value') else role


# =============================================================================
# Schemas
# =============================================================================

class UserSummary(BaseModel):
    id: UUID
    email: str
    name: str
    is_super_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationSummary(BaseModel):
    id: UUID
    name: str
    slug: str
    is_personal: bool
    is_active: bool
    member_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationDetail(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    logo_url: Optional[str]
    is_personal: bool
    is_active: bool
    settings: Optional[dict]
    created_at: datetime
    updated_at: datetime
    members: List["MemberSummary"]
    subscription: Optional["SubscriptionSummary"]

    class Config:
        from_attributes = True


class MemberSummary(BaseModel):
    id: UUID
    user_id: UUID
    user_email: str
    user_name: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscriptionSummary(BaseModel):
    id: UUID
    plan: str
    status: str
    current_period_end: Optional[datetime]

    class Config:
        from_attributes = True


class PlatformStats(BaseModel):
    total_users: int
    total_organizations: int
    total_subscriptions: int
    users_by_plan: dict
    recent_signups: int


class CreateOrganizationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None
    owner_user_id: UUID


class UpdateOrganizationRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    is_active: Optional[bool] = None
    settings: Optional[dict] = None


class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    is_super_admin: Optional[bool] = None


class AddMemberRequest(BaseModel):
    user_id: UUID
    role: OrganizationRole = OrganizationRole.MEMBER


class UpdateMemberRequest(BaseModel):
    role: OrganizationRole


class SetSubscriptionRequest(BaseModel):
    plan: PlanTier
    status: SubscriptionStatus = SubscriptionStatus.ACTIVE


# =============================================================================
# Platform Statistics
# =============================================================================

@router.get("/stats", response_model=PlatformStats)
async def get_platform_stats(
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get platform-wide statistics (super admin only)."""
    # Total users
    user_count = await db.execute(select(func.count(User.id)))
    total_users = user_count.scalar() or 0

    # Total organizations
    org_count = await db.execute(select(func.count(Organization.id)))
    total_organizations = org_count.scalar() or 0

    # Total subscriptions
    sub_count = await db.execute(select(func.count(Subscription.id)))
    total_subscriptions = sub_count.scalar() or 0

    # Users by plan
    plan_counts = await db.execute(
        select(Subscription.plan, func.count(Subscription.id))
        .group_by(Subscription.plan)
    )
    users_by_plan = {row[0].value if row[0] else "none": row[1] for row in plan_counts}

    # Recent signups (last 7 days)
    week_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    week_ago = week_ago - timedelta(days=7)
    recent_count = await db.execute(
        select(func.count(User.id)).where(User.created_at >= week_ago)
    )
    recent_signups = recent_count.scalar() or 0

    logger.info(f"Super admin {admin.email} retrieved platform stats")

    return PlatformStats(
        total_users=total_users,
        total_organizations=total_organizations,
        total_subscriptions=total_subscriptions,
        users_by_plan=users_by_plan,
        recent_signups=recent_signups
    )


# =============================================================================
# User Management
# =============================================================================

@router.get("/users", response_model=List[UserSummary])
async def list_users(
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    super_admins_only: bool = False
):
    """List all users (super admin only)."""
    query = select(User)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.email.ilike(search_pattern),
                User.name.ilike(search_pattern)
            )
        )

    if super_admins_only:
        query = query.where(User.is_super_admin == True)

    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    users = result.scalars().all()

    logger.info(f"Super admin {admin.email} listed users (count: {len(users)})")

    return [UserSummary.model_validate(u) for u in users]


@router.get("/users/{user_id}", response_model=UserSummary)
async def get_user(
    user_id: UUID,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user (super admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User", str(user_id))

    return UserSummary.model_validate(user)


@router.patch("/users/{user_id}", response_model=UserSummary)
async def update_user(
    user_id: UUID,
    data: UpdateUserRequest,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a user (super admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User", str(user_id))

    if data.name is not None:
        user.name = data.name

    if data.is_super_admin is not None:
        # Prevent removing own super admin status
        if user.id == admin.id and not data.is_super_admin:
            raise ValidationError("Cannot remove your own super admin status")
        user.is_super_admin = data.is_super_admin
        logger.warning(
            f"Super admin {admin.email} changed super admin status for {user.email} to {data.is_super_admin}"
        )

    await db.commit()
    await db.refresh(user)

    logger.info(f"Super admin {admin.email} updated user {user.email}")

    return UserSummary.model_validate(user)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: UUID,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a user (super admin only). Use with caution!"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundError("User", str(user_id))

    # Prevent self-deletion
    if user.id == admin.id:
        raise ValidationError("Cannot delete yourself")

    email = user.email
    await db.delete(user)
    await db.commit()

    logger.warning(f"Super admin {admin.email} deleted user {email}")

    return {"message": f"User {email} deleted"}


# =============================================================================
# Organization Management
# =============================================================================

@router.get("/organizations", response_model=List[OrganizationSummary])
async def list_organizations(
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    include_personal: bool = True
):
    """List all organizations (super admin only)."""
    query = select(Organization)

    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Organization.name.ilike(search_pattern),
                Organization.slug.ilike(search_pattern)
            )
        )

    if not include_personal:
        query = query.where(Organization.is_personal == False)

    query = query.order_by(Organization.created_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    orgs = result.scalars().all()

    # Get member counts
    summaries = []
    for org in orgs:
        member_count_result = await db.execute(
            select(func.count(OrganizationMember.id))
            .where(OrganizationMember.organization_id == org.id)
        )
        member_count = member_count_result.scalar() or 0

        summaries.append(OrganizationSummary(
            id=org.id,
            name=org.name,
            slug=org.slug,
            is_personal=org.is_personal,
            is_active=org.is_active,
            member_count=member_count,
            created_at=org.created_at
        ))

    logger.info(f"Super admin {admin.email} listed organizations (count: {len(summaries)})")

    return summaries


@router.get("/organizations/{org_id}", response_model=OrganizationDetail)
async def get_organization(
    org_id: UUID,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get organization details (super admin only)."""
    result = await db.execute(
        select(Organization)
        .options(
            selectinload(Organization.members).selectinload(OrganizationMember.user),
            selectinload(Organization.subscription)
        )
        .where(Organization.id == org_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise NotFoundError("Organization", str(org_id))

    members = [
        MemberSummary(
            id=m.id,
            user_id=m.user_id,
            user_email=m.user.email,
            user_name=m.user.name,
            role=get_role_value(m.role),
            is_active=m.is_active,
            created_at=m.created_at
        )
        for m in org.members
    ]

    subscription = None
    if org.subscription:
        subscription = SubscriptionSummary(
            id=org.subscription.id,
            plan=org.subscription.plan.value,
            status=org.subscription.status.value,
            current_period_end=org.subscription.current_period_end
        )

    return OrganizationDetail(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        is_personal=org.is_personal,
        is_active=org.is_active,
        settings=org.settings,
        created_at=org.created_at,
        updated_at=org.updated_at,
        members=members,
        subscription=subscription
    )


@router.post("/organizations", response_model=OrganizationSummary)
async def create_organization(
    data: CreateOrganizationRequest,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new organization (super admin only)."""
    # Check slug uniqueness
    existing = await db.execute(
        select(Organization).where(Organization.slug == data.slug)
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Organization with slug '{data.slug}' already exists")

    # Verify owner exists
    owner_result = await db.execute(select(User).where(User.id == data.owner_user_id))
    owner = owner_result.scalar_one_or_none()
    if not owner:
        raise NotFoundError("User", str(data.owner_user_id))

    # Create organization
    org = Organization(
        name=data.name,
        slug=data.slug,
        description=data.description,
        is_personal=False,
        is_active=True
    )
    db.add(org)
    await db.flush()

    # Add owner as member
    member = OrganizationMember(
        organization_id=org.id,
        user_id=owner.id,
        role=OrganizationRole.OWNER,
        is_active=True,
        accepted_at=datetime.utcnow()
    )
    db.add(member)

    await db.commit()
    await db.refresh(org)

    logger.info(f"Super admin {admin.email} created organization {org.name} (slug: {org.slug})")

    return OrganizationSummary(
        id=org.id,
        name=org.name,
        slug=org.slug,
        is_personal=org.is_personal,
        is_active=org.is_active,
        member_count=1,
        created_at=org.created_at
    )


@router.patch("/organizations/{org_id}", response_model=OrganizationSummary)
async def update_organization(
    org_id: UUID,
    data: UpdateOrganizationRequest,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update an organization (super admin only)."""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()

    if not org:
        raise NotFoundError("Organization", str(org_id))

    if data.name is not None:
        org.name = data.name
    if data.description is not None:
        org.description = data.description
    if data.is_active is not None:
        org.is_active = data.is_active
    if data.settings is not None:
        org.settings = data.settings

    await db.commit()
    await db.refresh(org)

    # Get member count
    member_count_result = await db.execute(
        select(func.count(OrganizationMember.id))
        .where(OrganizationMember.organization_id == org.id)
    )
    member_count = member_count_result.scalar() or 0

    logger.info(f"Super admin {admin.email} updated organization {org.name}")

    return OrganizationSummary(
        id=org.id,
        name=org.name,
        slug=org.slug,
        is_personal=org.is_personal,
        is_active=org.is_active,
        member_count=member_count,
        created_at=org.created_at
    )


@router.delete("/organizations/{org_id}")
async def delete_organization(
    org_id: UUID,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete an organization (super admin only). Use with extreme caution!"""
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()

    if not org:
        raise NotFoundError("Organization", str(org_id))

    name = org.name
    await db.delete(org)
    await db.commit()

    logger.warning(f"Super admin {admin.email} deleted organization {name}")

    return {"message": f"Organization {name} deleted"}


# =============================================================================
# Organization Member Management
# =============================================================================

@router.post("/organizations/{org_id}/members", response_model=MemberSummary)
async def add_member(
    org_id: UUID,
    data: AddMemberRequest,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Add a member to an organization (super admin only)."""
    # Verify organization exists
    org_result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = org_result.scalar_one_or_none()
    if not org:
        raise NotFoundError("Organization", str(org_id))

    # Verify user exists
    user_result = await db.execute(select(User).where(User.id == data.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User", str(data.user_id))

    # Check if already a member
    existing = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == data.user_id
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("User is already a member of this organization")

    member = OrganizationMember(
        organization_id=org_id,
        user_id=data.user_id,
        role=data.role,
        is_active=True,
        accepted_at=datetime.utcnow()
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)

    logger.info(
        f"Super admin {admin.email} added {user.email} to {org.name} as {data.role.value}"
    )

    return MemberSummary(
        id=member.id,
        user_id=member.user_id,
        user_email=user.email,
        user_name=user.name,
        role=get_role_value(member.role),
        is_active=member.is_active,
        created_at=member.created_at
    )


@router.patch("/organizations/{org_id}/members/{member_id}", response_model=MemberSummary)
async def update_member(
    org_id: UUID,
    member_id: UUID,
    data: UpdateMemberRequest,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a member's role (super admin only)."""
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.user))
        .where(
            OrganizationMember.id == member_id,
            OrganizationMember.organization_id == org_id
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise NotFoundError("Member", str(member_id))

    old_role = member.role
    member.role = data.role

    await db.commit()
    await db.refresh(member)

    logger.info(
        f"Super admin {admin.email} changed {member.user.email} role from {old_role.value} to {data.role.value}"
    )

    return MemberSummary(
        id=member.id,
        user_id=member.user_id,
        user_email=member.user.email,
        user_name=member.user.name,
        role=get_role_value(member.role),
        is_active=member.is_active,
        created_at=member.created_at
    )


@router.delete("/organizations/{org_id}/members/{member_id}")
async def remove_member(
    org_id: UUID,
    member_id: UUID,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Remove a member from an organization (super admin only)."""
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.user))
        .where(
            OrganizationMember.id == member_id,
            OrganizationMember.organization_id == org_id
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise NotFoundError("Member", str(member_id))

    email = member.user.email
    await db.delete(member)
    await db.commit()

    logger.info(f"Super admin {admin.email} removed {email} from organization {org_id}")

    return {"message": f"Member {email} removed"}


# =============================================================================
# Subscription Management
# =============================================================================

@router.post("/organizations/{org_id}/subscription", response_model=SubscriptionSummary)
async def set_organization_subscription(
    org_id: UUID,
    data: SetSubscriptionRequest,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Set or update an organization's subscription (super admin only)."""
    # Verify organization exists
    org_result = await db.execute(
        select(Organization)
        .options(selectinload(Organization.subscription))
        .where(Organization.id == org_id)
    )
    org = org_result.scalar_one_or_none()
    if not org:
        raise NotFoundError("Organization", str(org_id))

    if org.subscription:
        # Update existing subscription
        org.subscription.plan = data.plan
        org.subscription.status = data.status
        await db.commit()
        await db.refresh(org.subscription)
        subscription = org.subscription
    else:
        # Create new subscription
        subscription = Subscription(
            organization_id=org_id,
            plan=data.plan,
            status=data.status
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

    logger.info(
        f"Super admin {admin.email} set {org.name} subscription to {data.plan.value}"
    )

    return SubscriptionSummary(
        id=subscription.id,
        plan=subscription.plan.value,
        status=subscription.status.value,
        current_period_end=subscription.current_period_end
    )


@router.post("/users/{user_id}/subscription", response_model=SubscriptionSummary)
async def set_user_subscription(
    user_id: UUID,
    data: SetSubscriptionRequest,
    admin: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db)
):
    """Set or update a user's personal subscription (super admin only)."""
    # Verify user exists
    user_result = await db.execute(
        select(User)
        .options(selectinload(User.subscription))
        .where(User.id == user_id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise NotFoundError("User", str(user_id))

    if user.subscription:
        # Update existing subscription
        user.subscription.plan = data.plan
        user.subscription.status = data.status
        await db.commit()
        await db.refresh(user.subscription)
        subscription = user.subscription
    else:
        # Create new subscription
        subscription = Subscription(
            user_id=user_id,
            plan=data.plan,
            status=data.status
        )
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)

    logger.info(
        f"Super admin {admin.email} set {user.email} subscription to {data.plan.value}"
    )

    return SubscriptionSummary(
        id=subscription.id,
        plan=subscription.plan.value,
        status=subscription.status.value,
        current_period_end=subscription.current_period_end
    )
