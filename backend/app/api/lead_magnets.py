"""Lead magnet API routes for capturing and tracking leads."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import LeadMagnetLead, User

router = APIRouter()


# ============================================================================
# Schemas
# ============================================================================

class LeadMagnetCaptureRequest(BaseModel):
    """Request to capture a lead magnet signup."""
    email: EmailStr
    name: Optional[str] = None
    company: Optional[str] = None
    source: str  # e.g., "email-prompts", "triage-framework", etc.
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None


class LeadMagnetCaptureResponse(BaseModel):
    """Response after capturing a lead."""
    success: bool
    lead_id: str
    message: str
    is_new: bool  # True if new lead, False if existing


class LeadMagnetStatsResponse(BaseModel):
    """Stats for lead magnet performance."""
    total_leads: int
    by_source: dict[str, int]
    conversion_rate: float
    recent_leads: int  # last 7 days


# ============================================================================
# Routes
# ============================================================================

@router.post("/capture", response_model=LeadMagnetCaptureResponse)
async def capture_lead(
    request: Request,
    data: LeadMagnetCaptureRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Capture a lead magnet signup.

    This endpoint:
    1. Creates or updates a lead magnet lead record
    2. Tracks metadata (IP, user agent, UTM params)
    3. Returns success with lead ID

    Public endpoint - no auth required.
    """
    # Get metadata from request
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    # Normalize email
    email_lower = data.email.lower()

    # Check if lead already exists for this source
    stmt = select(LeadMagnetLead).where(
        LeadMagnetLead.email == email_lower,
        LeadMagnetLead.source == data.source
    )
    result = await db.execute(stmt)
    existing_lead = result.scalar_one_or_none()

    if existing_lead:
        # Update existing lead
        existing_lead.view_count += 1
        existing_lead.last_seen_at = datetime.utcnow()
        if data.name and not existing_lead.name:
            existing_lead.name = data.name
        if data.company and not existing_lead.company:
            existing_lead.company = data.company

        await db.commit()

        return LeadMagnetCaptureResponse(
            success=True,
            lead_id=str(existing_lead.id),
            message="Welcome back! Access granted.",
            is_new=False
        )

    # Create new lead
    new_lead = LeadMagnetLead(
        email=email_lower,
        name=data.name,
        company=data.company,
        source=data.source,
        ip_address=ip_address,
        user_agent=user_agent,
        utm_source=data.utm_source,
        utm_medium=data.utm_medium,
        utm_campaign=data.utm_campaign,
        view_count=1,
        last_seen_at=datetime.utcnow()
    )

    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)

    return LeadMagnetCaptureResponse(
        success=True,
        lead_id=str(new_lead.id),
        message="Success! Check your email for the download link.",
        is_new=True
    )


@router.post("/track-download/{lead_id}")
async def track_download(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Track when a lead downloads the resource.

    Public endpoint - called from thank you page.
    """
    stmt = select(LeadMagnetLead).where(LeadMagnetLead.id == lead_id)
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    lead.download_count += 1
    lead.last_seen_at = datetime.utcnow()

    await db.commit()

    return {"success": True, "downloads": lead.download_count}


@router.post("/track-conversion")
async def track_conversion(
    email: EmailStr,
    user_id: UUID,
    conversion_type: str,  # "trial" or "paid"
    db: AsyncSession = Depends(get_db)
):
    """
    Track when a lead magnet lead converts to a user.

    Called from registration/signup flow.
    Internal endpoint - should be called from auth service.
    """
    # Find all unconverted leads with this email
    stmt = select(LeadMagnetLead).where(
        LeadMagnetLead.email == email.lower(),
        LeadMagnetLead.converted_at.is_(None)
    )
    result = await db.execute(stmt)
    leads = result.scalars().all()

    if not leads:
        return {"success": True, "converted": 0, "message": "No leads found"}

    # Mark all as converted
    for lead in leads:
        lead.converted_at = datetime.utcnow()
        lead.converted_to = conversion_type
        lead.converted_user_id = user_id

    await db.commit()

    return {
        "success": True,
        "converted": len(leads),
        "message": f"Marked {len(leads)} leads as converted"
    }


@router.get("/stats", response_model=LeadMagnetStatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db)
):
    """
    Get lead magnet performance stats.

    Public endpoint for dashboard/admin.
    """
    # Total leads
    total_stmt = select(func.count(LeadMagnetLead.id))
    total_result = await db.execute(total_stmt)
    total_leads = total_result.scalar() or 0

    # By source
    source_stmt = select(
        LeadMagnetLead.source,
        func.count(LeadMagnetLead.id)
    ).group_by(LeadMagnetLead.source)
    source_result = await db.execute(source_stmt)
    by_source = {source: count for source, count in source_result}

    # Conversion rate
    converted_stmt = select(func.count(LeadMagnetLead.id)).where(
        LeadMagnetLead.converted_at.isnot(None)
    )
    converted_result = await db.execute(converted_stmt)
    converted_count = converted_result.scalar() or 0
    conversion_rate = (converted_count / total_leads * 100) if total_leads > 0 else 0.0

    # Recent leads (last 7 days)
    seven_days_ago = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    from datetime import timedelta
    seven_days_ago = seven_days_ago - timedelta(days=7)

    recent_stmt = select(func.count(LeadMagnetLead.id)).where(
        LeadMagnetLead.created_at >= seven_days_ago
    )
    recent_result = await db.execute(recent_stmt)
    recent_leads = recent_result.scalar() or 0

    return LeadMagnetStatsResponse(
        total_leads=total_leads,
        by_source=by_source,
        conversion_rate=conversion_rate,
        recent_leads=recent_leads
    )


@router.get("/check-access/{source}")
async def check_access(
    source: str,
    email: EmailStr,
    db: AsyncSession = Depends(get_db)
):
    """
    Check if an email has access to a specific lead magnet.

    Used for gated content - returns access status.
    Public endpoint.
    """
    stmt = select(LeadMagnetLead).where(
        LeadMagnetLead.email == email.lower(),
        LeadMagnetLead.source == source
    )
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()

    return {
        "has_access": lead is not None,
        "lead_id": str(lead.id) if lead else None
    }
