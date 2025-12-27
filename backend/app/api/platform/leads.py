"""
Platform Leads Inbound Endpoint
Receives leads from get-platform (Meta, Snap, TikTok ad campaigns)
"""

import os
import uuid
import httpx
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization, OrganizationMember
from app.core.security import hash_password

router = APIRouter()

PLATFORM_API_KEY = os.getenv("PLATFORM_API_KEY")
GETMAILER_URL = os.getenv("GETMAILER_URL", "https://getmailer.io")
GETMAILER_ENROLL_KEY = os.getenv("GETMAILER_ENROLL_KEY")


class LeadData(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    fullName: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None


class InboundLeadRequest(BaseModel):
    source: str  # 'meta' | 'snapchat' | 'tiktok'
    sourceLeadId: str
    formId: str
    adId: Optional[str] = None
    campaignId: Optional[str] = None
    getmailerSequence: Optional[str] = None
    lead: LeadData


class InboundLeadResponse(BaseModel):
    success: bool
    userId: Optional[str] = None
    organizationId: Optional[str] = None
    isNew: Optional[bool] = None
    message: Optional[str] = None


def generate_secure_password() -> str:
    """Generate a secure temporary password"""
    import secrets
    import string
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(chars) for _ in range(12))


async def enroll_in_getmailer(
    email: str,
    first_name: Optional[str],
    last_name: Optional[str],
    sequence_id: str,
    variables: Optional[dict] = None
):
    """Enroll user in GetMailer sequence"""
    if not GETMAILER_ENROLL_KEY:
        return

    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{GETMAILER_URL}/api/public/enroll",
                headers={
                    "Content-Type": "application/json",
                    "X-Enroll-Key": GETMAILER_ENROLL_KEY,
                },
                json={
                    "email": email,
                    "firstName": first_name,
                    "lastName": last_name,
                    "sequenceId": sequence_id,
                    "variables": variables or {},
                    "project": "getanswers",
                    "source": "ad-platform-lead",
                },
                timeout=10.0
            )
    except Exception as e:
        print(f"[GetMailer] Enrollment error: {e}")


@router.post("/leads/inbound", response_model=InboundLeadResponse)
async def inbound_lead(
    request: InboundLeadRequest,
    x_platform_api_key: str = Header(..., alias="X-Platform-API-Key"),
    db: AsyncSession = Depends(get_db)
):
    """
    Receive inbound leads from get-platform
    Creates user and organization if they don't exist
    """
    # Validate API key
    if x_platform_api_key != PLATFORM_API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

    lead = request.lead

    if not lead.email:
        raise HTTPException(status_code=400, detail="Email is required")

    email = lead.email.lower().strip()

    # Check for existing user
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        # Get organization
        org_result = await db.execute(
            select(OrganizationMember)
            .where(OrganizationMember.user_id == existing_user.id)
            .limit(1)
        )
        org_member = org_result.scalar_one_or_none()

        return InboundLeadResponse(
            success=True,
            userId=str(existing_user.id),
            organizationId=str(org_member.organization_id) if org_member else None,
            isNew=False,
            message="User already exists"
        )

    # Generate temp password
    temp_password = generate_secure_password()
    password_hash = hash_password(temp_password)

    # Build name
    name = (
        lead.fullName or
        (f"{lead.firstName} {lead.lastName}" if lead.firstName and lead.lastName else None) or
        lead.firstName or
        email.split('@')[0]
    )

    # Create organization
    org_id = str(uuid.uuid4())
    org_slug = f"{(lead.company or name).lower().replace(' ', '-')[:20]}-{uuid.uuid4().hex[:8]}"

    org = Organization(
        id=org_id,
        name=lead.company or f"{name}'s Organization",
        slug=org_slug,
        is_active=True,
        is_personal=not lead.company,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(org)

    # Create user
    user_id = str(uuid.uuid4())
    user = User(
        id=user_id,
        email=email,
        name=name,
        password_hash=password_hash,
        current_organization_id=org_id,
        needs_password_setup=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)

    # Create membership
    membership = OrganizationMember(
        id=str(uuid.uuid4()),
        organization_id=org_id,
        user_id=user_id,
        role="OWNER",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(membership)

    await db.commit()

    # Enroll in GetMailer sequence (fire and forget)
    if request.getmailerSequence:
        import asyncio
        asyncio.create_task(enroll_in_getmailer(
            email=email,
            first_name=lead.firstName,
            last_name=lead.lastName,
            sequence_id=request.getmailerSequence,
            variables={"tempPassword": temp_password}
        ))

    return InboundLeadResponse(
        success=True,
        userId=user_id,
        organizationId=org_id,
        isNew=True
    )
