"""Organization management API endpoints."""
import secrets
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ConflictError, ValidationError, AuthorizationError
from app.core.logging import logger
from app.api.deps import (
    get_current_user, get_current_organization, get_org_membership,
    require_org_admin, require_org_owner
)
from app.models import (
    User, Organization, OrganizationMember, OrganizationInvite,
    OrganizationRole, Subscription, PlanTier
)

router = APIRouter()


# =============================================================================
# Schemas
# =============================================================================

class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    logo_url: Optional[str]
    is_personal: bool
    is_active: bool
    member_count: int
    my_role: str
    created_at: datetime

    class Config:
        from_attributes = True


class OrganizationListItem(BaseModel):
    id: UUID
    name: str
    slug: str
    is_personal: bool
    my_role: str


class MemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    email: str
    name: str
    role: str
    is_active: bool
    joined_at: datetime

    class Config:
        from_attributes = True


class InviteResponse(BaseModel):
    id: UUID
    email: str
    role: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class CreateOrganizationRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    slug: str = Field(..., min_length=1, max_length=100, pattern=r"^[a-z0-9-]+$")
    description: Optional[str] = None


class UpdateOrganizationRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    logo_url: Optional[str] = None
    settings: Optional[dict] = None


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: OrganizationRole = OrganizationRole.MEMBER


class UpdateMemberRoleRequest(BaseModel):
    role: OrganizationRole


class SwitchOrganizationRequest(BaseModel):
    organization_id: UUID


# =============================================================================
# Organization CRUD
# =============================================================================

@router.get("/", response_model=List[OrganizationListItem])
async def list_my_organizations(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all organizations the current user is a member of."""
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.organization))
        .where(
            OrganizationMember.user_id == user.id,
            OrganizationMember.is_active == True
        )
        .order_by(OrganizationMember.created_at)
    )
    memberships = result.scalars().all()

    return [
        OrganizationListItem(
            id=m.organization.id,
            name=m.organization.name,
            slug=m.organization.slug,
            is_personal=m.organization.is_personal,
            my_role=m.role.value
        )
        for m in memberships
    ]


@router.get("/current", response_model=OrganizationResponse)
async def get_current_org(
    organization: Organization = Depends(get_current_organization),
    member: OrganizationMember = Depends(get_org_membership),
    db: AsyncSession = Depends(get_db)
):
    """Get the current organization context."""
    # Get member count
    member_count_result = await db.execute(
        select(func.count(OrganizationMember.id))
        .where(
            OrganizationMember.organization_id == organization.id,
            OrganizationMember.is_active == True
        )
    )
    member_count = member_count_result.scalar() or 0

    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        description=organization.description,
        logo_url=organization.logo_url,
        is_personal=organization.is_personal,
        is_active=organization.is_active,
        member_count=member_count,
        my_role=member.role.value,
        created_at=organization.created_at
    )


@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    data: CreateOrganizationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new organization. The creating user becomes the owner."""
    # Check slug uniqueness
    existing = await db.execute(
        select(Organization).where(Organization.slug == data.slug)
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Organization with slug '{data.slug}' already exists")

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

    # Add creator as owner
    member = OrganizationMember(
        organization_id=org.id,
        user_id=user.id,
        role=OrganizationRole.OWNER,
        is_active=True,
        accepted_at=datetime.utcnow()
    )
    db.add(member)

    await db.commit()
    await db.refresh(org)

    logger.info(f"User {user.email} created organization {org.name}")

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        description=org.description,
        logo_url=org.logo_url,
        is_personal=org.is_personal,
        is_active=org.is_active,
        member_count=1,
        my_role=OrganizationRole.OWNER.value,
        created_at=org.created_at
    )


@router.patch("/current", response_model=OrganizationResponse)
async def update_current_organization(
    data: UpdateOrganizationRequest,
    organization: Organization = Depends(get_current_organization),
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update the current organization (admin+ only)."""
    if data.name is not None:
        organization.name = data.name
    if data.description is not None:
        organization.description = data.description
    if data.logo_url is not None:
        organization.logo_url = data.logo_url
    if data.settings is not None:
        organization.settings = data.settings

    await db.commit()
    await db.refresh(organization)

    # Get member count
    member_count_result = await db.execute(
        select(func.count(OrganizationMember.id))
        .where(
            OrganizationMember.organization_id == organization.id,
            OrganizationMember.is_active == True
        )
    )
    member_count = member_count_result.scalar() or 0

    logger.info(f"Organization {organization.name} updated by {member.user_id}")

    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        slug=organization.slug,
        description=organization.description,
        logo_url=organization.logo_url,
        is_personal=organization.is_personal,
        is_active=organization.is_active,
        member_count=member_count,
        my_role=member.role.value,
        created_at=organization.created_at
    )


@router.post("/switch")
async def switch_organization(
    data: SwitchOrganizationRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Switch the user's current organization context."""
    # Verify membership
    result = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == data.organization_id,
            OrganizationMember.user_id == user.id,
            OrganizationMember.is_active == True
        )
    )
    member = result.scalar_one_or_none()

    if not member and not user.is_super_admin:
        raise AuthorizationError("Not a member of this organization")

    user.current_organization_id = data.organization_id
    await db.commit()

    logger.info(f"User {user.email} switched to organization {data.organization_id}")

    return {"message": "Organization switched", "organization_id": str(data.organization_id)}


# =============================================================================
# Member Management
# =============================================================================

@router.get("/members", response_model=List[MemberResponse])
async def list_members(
    organization: Organization = Depends(get_current_organization),
    member: OrganizationMember = Depends(get_org_membership),
    db: AsyncSession = Depends(get_db)
):
    """List all members of the current organization."""
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.user))
        .where(
            OrganizationMember.organization_id == organization.id,
            OrganizationMember.is_active == True
        )
        .order_by(OrganizationMember.created_at)
    )
    members = result.scalars().all()

    return [
        MemberResponse(
            id=m.id,
            user_id=m.user_id,
            email=m.user.email,
            name=m.user.name,
            role=m.role.value,
            is_active=m.is_active,
            joined_at=m.accepted_at or m.created_at
        )
        for m in members
    ]


@router.patch("/members/{member_id}", response_model=MemberResponse)
async def update_member_role(
    member_id: UUID,
    data: UpdateMemberRoleRequest,
    organization: Organization = Depends(get_current_organization),
    current_member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a member's role (admin+ only)."""
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.user))
        .where(
            OrganizationMember.id == member_id,
            OrganizationMember.organization_id == organization.id
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise NotFoundError("Member", str(member_id))

    # Prevent demoting owner unless you're also an owner
    if member.role == OrganizationRole.OWNER and current_member.role != OrganizationRole.OWNER:
        raise AuthorizationError("Only owners can change owner roles")

    # Prevent promoting to owner unless you're an owner
    if data.role == OrganizationRole.OWNER and current_member.role != OrganizationRole.OWNER:
        raise AuthorizationError("Only owners can promote to owner")

    # Prevent demoting yourself if you're the last owner
    if member.user_id == current_member.user_id and member.role == OrganizationRole.OWNER:
        owner_count = await db.execute(
            select(func.count(OrganizationMember.id)).where(
                OrganizationMember.organization_id == organization.id,
                OrganizationMember.role == OrganizationRole.OWNER,
                OrganizationMember.is_active == True
            )
        )
        if owner_count.scalar() <= 1 and data.role != OrganizationRole.OWNER:
            raise ValidationError("Cannot demote the last owner")

    member.role = data.role
    await db.commit()
    await db.refresh(member)

    logger.info(f"Member {member.user.email} role changed to {data.role.value}")

    return MemberResponse(
        id=member.id,
        user_id=member.user_id,
        email=member.user.email,
        name=member.user.name,
        role=member.role.value,
        is_active=member.is_active,
        joined_at=member.accepted_at or member.created_at
    )


@router.delete("/members/{member_id}")
async def remove_member(
    member_id: UUID,
    organization: Organization = Depends(get_current_organization),
    current_member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db)
):
    """Remove a member from the organization (admin+ only)."""
    result = await db.execute(
        select(OrganizationMember)
        .options(selectinload(OrganizationMember.user))
        .where(
            OrganizationMember.id == member_id,
            OrganizationMember.organization_id == organization.id
        )
    )
    member = result.scalar_one_or_none()

    if not member:
        raise NotFoundError("Member", str(member_id))

    # Prevent removing owner unless you're also an owner
    if member.role == OrganizationRole.OWNER and current_member.role != OrganizationRole.OWNER:
        raise AuthorizationError("Only owners can remove owners")

    # Prevent removing yourself if you're the last owner
    if member.user_id == current_member.user_id and member.role == OrganizationRole.OWNER:
        owner_count = await db.execute(
            select(func.count(OrganizationMember.id)).where(
                OrganizationMember.organization_id == organization.id,
                OrganizationMember.role == OrganizationRole.OWNER,
                OrganizationMember.is_active == True
            )
        )
        if owner_count.scalar() <= 1:
            raise ValidationError("Cannot remove the last owner")

    email = member.user.email
    await db.delete(member)
    await db.commit()

    logger.info(f"Member {email} removed from organization {organization.name}")

    return {"message": f"Member {email} removed"}


# =============================================================================
# Invitations
# =============================================================================

@router.get("/invites", response_model=List[InviteResponse])
async def list_invites(
    organization: Organization = Depends(get_current_organization),
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db)
):
    """List pending invitations (admin+ only)."""
    result = await db.execute(
        select(OrganizationInvite).where(
            OrganizationInvite.organization_id == organization.id,
            OrganizationInvite.accepted_at == None,
            OrganizationInvite.expires_at > datetime.utcnow()
        )
        .order_by(OrganizationInvite.created_at.desc())
    )
    invites = result.scalars().all()

    return [
        InviteResponse(
            id=i.id,
            email=i.email,
            role=i.role.value,
            expires_at=i.expires_at,
            created_at=i.created_at
        )
        for i in invites
    ]


@router.post("/invites", response_model=InviteResponse)
async def create_invite(
    data: InviteMemberRequest,
    organization: Organization = Depends(get_current_organization),
    member: OrganizationMember = Depends(require_org_admin),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create an invitation to join the organization (admin+ only)."""
    # Check if user already exists and is a member
    existing_user = await db.execute(
        select(User).where(User.email == data.email)
    )
    existing_user = existing_user.scalar_one_or_none()

    if existing_user:
        existing_member = await db.execute(
            select(OrganizationMember).where(
                OrganizationMember.organization_id == organization.id,
                OrganizationMember.user_id == existing_user.id
            )
        )
        if existing_member.scalar_one_or_none():
            raise ConflictError("User is already a member of this organization")

    # Check for existing pending invite
    existing_invite = await db.execute(
        select(OrganizationInvite).where(
            OrganizationInvite.organization_id == organization.id,
            OrganizationInvite.email == data.email,
            OrganizationInvite.accepted_at == None,
            OrganizationInvite.expires_at > datetime.utcnow()
        )
    )
    if existing_invite.scalar_one_or_none():
        raise ConflictError("An active invitation already exists for this email")

    # Prevent inviting as owner unless you're an owner
    if data.role == OrganizationRole.OWNER and member.role != OrganizationRole.OWNER:
        raise AuthorizationError("Only owners can invite as owner")

    # Create invite
    invite = OrganizationInvite(
        organization_id=organization.id,
        email=data.email,
        role=data.role,
        token=secrets.token_urlsafe(32),
        invited_by_id=user.id,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(invite)
    await db.commit()
    await db.refresh(invite)

    # TODO: Send invitation email

    logger.info(f"Invitation sent to {data.email} for organization {organization.name}")

    return InviteResponse(
        id=invite.id,
        email=invite.email,
        role=invite.role.value,
        expires_at=invite.expires_at,
        created_at=invite.created_at
    )


@router.delete("/invites/{invite_id}")
async def cancel_invite(
    invite_id: UUID,
    organization: Organization = Depends(get_current_organization),
    member: OrganizationMember = Depends(require_org_admin),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a pending invitation (admin+ only)."""
    result = await db.execute(
        select(OrganizationInvite).where(
            OrganizationInvite.id == invite_id,
            OrganizationInvite.organization_id == organization.id
        )
    )
    invite = result.scalar_one_or_none()

    if not invite:
        raise NotFoundError("Invite", str(invite_id))

    email = invite.email
    await db.delete(invite)
    await db.commit()

    logger.info(f"Invitation to {email} cancelled for organization {organization.name}")

    return {"message": f"Invitation to {email} cancelled"}


@router.post("/invites/accept")
async def accept_invite(
    token: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Accept an organization invitation."""
    result = await db.execute(
        select(OrganizationInvite)
        .options(selectinload(OrganizationInvite.organization))
        .where(OrganizationInvite.token == token)
    )
    invite = result.scalar_one_or_none()

    if not invite:
        raise NotFoundError("Invite", "token")

    if invite.is_expired:
        raise ValidationError("This invitation has expired")

    if invite.is_accepted:
        raise ValidationError("This invitation has already been used")

    if invite.email.lower() != user.email.lower():
        raise AuthorizationError("This invitation is for a different email address")

    # Check if already a member
    existing = await db.execute(
        select(OrganizationMember).where(
            OrganizationMember.organization_id == invite.organization_id,
            OrganizationMember.user_id == user.id
        )
    )
    if existing.scalar_one_or_none():
        # Mark invite as accepted anyway
        invite.accepted_at = datetime.utcnow()
        await db.commit()
        raise ConflictError("You are already a member of this organization")

    # Create membership
    member = OrganizationMember(
        organization_id=invite.organization_id,
        user_id=user.id,
        role=invite.role,
        invited_by_id=invite.invited_by_id,
        invited_at=invite.created_at,
        accepted_at=datetime.utcnow(),
        is_active=True
    )
    db.add(member)

    # Mark invite as accepted
    invite.accepted_at = datetime.utcnow()

    await db.commit()

    logger.info(f"User {user.email} accepted invitation to {invite.organization.name}")

    return {
        "message": f"Welcome to {invite.organization.name}!",
        "organization_id": str(invite.organization_id),
        "organization_name": invite.organization.name
    }


# =============================================================================
# Leave Organization
# =============================================================================

@router.post("/leave")
async def leave_organization(
    organization: Organization = Depends(get_current_organization),
    member: OrganizationMember = Depends(get_org_membership),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Leave the current organization."""
    # Prevent leaving if you're the last owner
    if member.role == OrganizationRole.OWNER:
        owner_count = await db.execute(
            select(func.count(OrganizationMember.id)).where(
                OrganizationMember.organization_id == organization.id,
                OrganizationMember.role == OrganizationRole.OWNER,
                OrganizationMember.is_active == True
            )
        )
        if owner_count.scalar() <= 1:
            raise ValidationError(
                "Cannot leave: you are the last owner. Transfer ownership first or delete the organization."
            )

    # Remove membership
    await db.delete(member)

    # Clear current org if it was this one
    if user.current_organization_id == organization.id:
        user.current_organization_id = None

    await db.commit()

    logger.info(f"User {user.email} left organization {organization.name}")

    return {"message": f"You have left {organization.name}"}
