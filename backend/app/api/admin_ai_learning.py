"""Admin AI Learning Analytics - Platform-wide metrics for AI learning system.

This module provides super admin endpoints to monitor:
- AI learning adoption rates
- Profile quality metrics
- Edit pattern trends
- System performance
- Cost tracking
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, case, cast
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timedelta
import json

from app.core.database import get_db
from app.core.logging import logger
from app.api.deps import get_current_user, require_super_admin
from app.models.user import User
from app.models.agent_action import AgentAction, ActionStatus
from app.models.conversation import Conversation
from app.models.objective import Objective
from app.models.message import Message, MessageDirection


router = APIRouter()


# =============================================================================
# Pydantic Schemas
# =============================================================================

class AILearningOverview(BaseModel):
    """Platform-wide AI learning overview."""
    total_users: int
    users_with_profiles: int
    profile_coverage_percent: float
    avg_profile_confidence: float
    avg_sample_size: float

    total_edits_all_time: int
    edits_last_30_days: int
    users_with_edits: int
    avg_edit_percentage: float

    stale_profiles_count: int  # >30 days old
    users_needing_analysis: int  # Has emails but no profile


class ProfileQualityMetrics(BaseModel):
    """Profile quality distribution."""
    high_confidence: int  # >80%
    medium_confidence: int  # 50-80%
    low_confidence: int  # <50%

    large_sample: int  # >30 emails
    medium_sample: int  # 10-30 emails
    small_sample: int  # <10 emails


class EditPatternInsights(BaseModel):
    """Platform-wide edit pattern insights."""
    avg_edit_rate_all_users: float  # % of drafts that get edited
    heavy_edit_rate: float  # % of edits changing >50%

    common_edit_types: List[dict]  # Most common edit patterns
    users_improving: int  # Users with decreasing edit rates
    users_struggling: int  # Users with increasing edit rates


class LearningEffectivenessMetrics(BaseModel):
    """Metrics showing learning effectiveness."""
    autonomous_rate_with_profile: float
    autonomous_rate_without_profile: float
    improvement_from_learning: float  # Percentage point improvement

    avg_confidence_with_profile: float
    avg_confidence_without_profile: float

    edit_rate_with_profile: float
    edit_rate_without_profile: float


class SystemPerformanceMetrics(BaseModel):
    """System performance and cost metrics."""
    analyses_last_7_days: int
    analyses_last_30_days: int

    avg_analysis_duration_seconds: float
    failed_analyses_count: int
    success_rate_percent: float

    estimated_monthly_cost_usd: float


class UserLearningDetail(BaseModel):
    """Detailed learning info for a specific user."""
    user_id: str
    email: str
    name: str

    has_profile: bool
    profile_confidence: Optional[float]
    sample_size: Optional[int]
    last_updated: Optional[datetime]

    total_edits: int
    recent_edits: int  # Last 30 days
    avg_edit_percentage: Optional[float]

    autonomous_rate: Optional[float]
    needs_analysis: bool


# =============================================================================
# API Endpoints
# =============================================================================

@router.get("/overview", response_model=AILearningOverview)
async def get_ai_learning_overview(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get platform-wide overview of AI learning system.

    Shows adoption rates, profile quality, edit statistics.
    """
    # Total users and profile coverage
    total_users_query = select(func.count(User.id))
    result = await db.execute(total_users_query)
    total_users = result.scalar() or 0

    users_with_profiles_query = select(func.count(User.id)).where(
        User.writing_style_profile.isnot(None)
    )
    result = await db.execute(users_with_profiles_query)
    users_with_profiles = result.scalar() or 0

    profile_coverage = (users_with_profiles / total_users * 100) if total_users > 0 else 0.0

    # Average profile metrics
    # Parse JSON to get confidence and sample size
    avg_metrics_query = select(User.writing_style_profile).where(
        User.writing_style_profile.isnot(None)
    )
    result = await db.execute(avg_metrics_query)
    profiles = result.scalars().all()

    total_confidence = 0.0
    total_sample_size = 0
    valid_profiles = 0
    stale_count = 0
    cutoff_date = datetime.utcnow() - timedelta(days=30)

    for profile_str in profiles:
        try:
            profile = json.loads(profile_str)
            total_confidence += profile.get('confidence', 0.0)
            total_sample_size += profile.get('sample_size', 0)
            valid_profiles += 1

            # Check if stale
            last_updated_str = profile.get('last_updated')
            if last_updated_str:
                last_updated = datetime.fromisoformat(last_updated_str)
                if last_updated < cutoff_date:
                    stale_count += 1
        except:
            continue

    avg_confidence = (total_confidence / valid_profiles) if valid_profiles > 0 else 0.0
    avg_sample = (total_sample_size / valid_profiles) if valid_profiles > 0 else 0.0

    # Edit statistics
    total_edits_query = select(func.count(AgentAction.id)).where(
        AgentAction.status == ActionStatus.EDITED
    )
    result = await db.execute(total_edits_query)
    total_edits = result.scalar() or 0

    recent_edits_query = select(func.count(AgentAction.id)).where(
        and_(
            AgentAction.status == ActionStatus.EDITED,
            AgentAction.approved_at >= datetime.utcnow() - timedelta(days=30)
        )
    )
    result = await db.execute(recent_edits_query)
    recent_edits = result.scalar() or 0

    users_with_edits_query = (
        select(func.count(func.distinct(Objective.user_id)))
        .select_from(AgentAction)
        .join(Conversation, AgentAction.conversation_id == Conversation.id)
        .join(Objective, Conversation.objective_id == Objective.id)
        .where(AgentAction.status == ActionStatus.EDITED)
    )
    result = await db.execute(users_with_edits_query)
    users_with_edits = result.scalar() or 0

    # Users needing analysis (have sent emails but no profile)
    users_needing_query = (
        select(func.count(func.distinct(User.id)))
        .select_from(User)
        .join(Objective, Objective.user_id == User.id)
        .join(Conversation, Conversation.objective_id == Objective.id)
        .join(Message, Message.conversation_id == Conversation.id)
        .where(
            and_(
                User.writing_style_profile.is_(None),
                Message.direction == MessageDirection.OUTGOING,
                User.email_provider.isnot(None)
            )
        )
    )
    result = await db.execute(users_needing_query)
    users_needing = result.scalar() or 0

    return AILearningOverview(
        total_users=total_users,
        users_with_profiles=users_with_profiles,
        profile_coverage_percent=round(profile_coverage, 1),
        avg_profile_confidence=round(avg_confidence, 2),
        avg_sample_size=round(avg_sample, 1),
        total_edits_all_time=total_edits,
        edits_last_30_days=recent_edits,
        users_with_edits=users_with_edits,
        avg_edit_percentage=0.0,  # Would need to calculate from edit diffs
        stale_profiles_count=stale_count,
        users_needing_analysis=users_needing
    )


@router.get("/profile-quality", response_model=ProfileQualityMetrics)
async def get_profile_quality_metrics(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get distribution of profile quality metrics.

    Shows how many profiles are high/medium/low quality by confidence and sample size.
    """
    # Get all profiles
    query = select(User.writing_style_profile).where(
        User.writing_style_profile.isnot(None)
    )
    result = await db.execute(query)
    profiles = result.scalars().all()

    high_conf = 0
    med_conf = 0
    low_conf = 0

    large_sample = 0
    med_sample = 0
    small_sample = 0

    for profile_str in profiles:
        try:
            profile = json.loads(profile_str)
            confidence = profile.get('confidence', 0.0)
            sample_size = profile.get('sample_size', 0)

            # Confidence buckets
            if confidence > 0.8:
                high_conf += 1
            elif confidence > 0.5:
                med_conf += 1
            else:
                low_conf += 1

            # Sample size buckets
            if sample_size > 30:
                large_sample += 1
            elif sample_size > 10:
                med_sample += 1
            else:
                small_sample += 1
        except:
            continue

    return ProfileQualityMetrics(
        high_confidence=high_conf,
        medium_confidence=med_conf,
        low_confidence=low_conf,
        large_sample=large_sample,
        medium_sample=med_sample,
        small_sample=small_sample
    )


@router.get("/users", response_model=List[UserLearningDetail])
async def get_users_learning_details(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    has_profile: Optional[bool] = None,
    needs_analysis: Optional[bool] = None,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed learning information for all users.

    Supports filtering by profile status and pagination.
    """
    # Build base query
    query = select(User).where(User.email_provider.isnot(None))

    if has_profile is not None:
        if has_profile:
            query = query.where(User.writing_style_profile.isnot(None))
        else:
            query = query.where(User.writing_style_profile.is_(None))

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    users = result.scalars().all()

    user_details = []

    for user in users:
        # Parse profile if exists
        has_prof = bool(user.writing_style_profile)
        prof_conf = None
        samp_size = None
        last_upd = None

        if has_prof:
            try:
                profile = json.loads(user.writing_style_profile)
                prof_conf = profile.get('confidence')
                samp_size = profile.get('sample_size')
                last_upd_str = profile.get('last_updated')
                if last_upd_str:
                    last_upd = datetime.fromisoformat(last_upd_str)
            except:
                pass

        # Count edits
        total_edits_query = (
            select(func.count(AgentAction.id))
            .select_from(AgentAction)
            .join(Conversation, AgentAction.conversation_id == Conversation.id)
            .join(Objective, Conversation.objective_id == Objective.id)
            .where(
                and_(
                    Objective.user_id == user.id,
                    AgentAction.status == ActionStatus.EDITED
                )
            )
        )
        result_edits = await db.execute(total_edits_query)
        total_edits = result_edits.scalar() or 0

        recent_edits_query = (
            select(func.count(AgentAction.id))
            .select_from(AgentAction)
            .join(Conversation, AgentAction.conversation_id == Conversation.id)
            .join(Objective, Conversation.objective_id == Objective.id)
            .where(
                and_(
                    Objective.user_id == user.id,
                    AgentAction.status == ActionStatus.EDITED,
                    AgentAction.approved_at >= datetime.utcnow() - timedelta(days=30)
                )
            )
        )
        result_recent = await db.execute(recent_edits_query)
        recent_edits = result_recent.scalar() or 0

        # Check if needs analysis
        sent_count_query = (
            select(func.count(Message.id))
            .select_from(Message)
            .join(Conversation, Message.conversation_id == Conversation.id)
            .join(Objective, Conversation.objective_id == Objective.id)
            .where(
                and_(
                    Objective.user_id == user.id,
                    Message.direction == MessageDirection.OUTGOING
                )
            )
        )
        result_sent = await db.execute(sent_count_query)
        sent_count = result_sent.scalar() or 0

        needs_anal = not has_prof and sent_count >= 3

        user_details.append(UserLearningDetail(
            user_id=str(user.id),
            email=user.email,
            name=user.name,
            has_profile=has_prof,
            profile_confidence=prof_conf,
            sample_size=samp_size,
            last_updated=last_upd,
            total_edits=total_edits,
            recent_edits=recent_edits,
            avg_edit_percentage=None,  # Would need to calculate
            autonomous_rate=None,  # Would need to calculate
            needs_analysis=needs_anal
        ))

    # Filter by needs_analysis if specified
    if needs_analysis is not None:
        user_details = [u for u in user_details if u.needs_analysis == needs_analysis]

    return user_details


@router.get("/system-performance", response_model=SystemPerformanceMetrics)
async def get_system_performance_metrics(
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Get system performance metrics for AI learning.

    Shows analysis frequency, success rates, estimated costs.

    Note: This is a placeholder that tracks profile updates.
    In production, would integrate with Celery task monitoring.
    """
    # Count recent profile updates as proxy for analyses
    # In production, would query Celery task results

    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Get all profiles
    query = select(User.writing_style_profile).where(
        User.writing_style_profile.isnot(None)
    )
    result = await db.execute(query)
    profiles = result.scalars().all()

    analyses_7d = 0
    analyses_30d = 0

    for profile_str in profiles:
        try:
            profile = json.loads(profile_str)
            last_updated_str = profile.get('last_updated')
            if last_updated_str:
                last_updated = datetime.fromisoformat(last_updated_str)
                if last_updated >= seven_days_ago:
                    analyses_7d += 1
                if last_updated >= thirty_days_ago:
                    analyses_30d += 1
        except:
            continue

    # Estimate costs
    # Assume:
    # - Writing style analysis: ~50 emails @ 500 words = 25,000 tokens input
    # - Claude Opus 4.5: $15/million input tokens
    # - Total: ~$0.30 per analysis
    cost_per_analysis = 0.30
    estimated_monthly_cost = analyses_30d * cost_per_analysis

    return SystemPerformanceMetrics(
        analyses_last_7_days=analyses_7d,
        analyses_last_30_days=analyses_30d,
        avg_analysis_duration_seconds=15.0,  # Placeholder
        failed_analyses_count=0,  # Would need Celery monitoring
        success_rate_percent=100.0,  # Would need Celery monitoring
        estimated_monthly_cost_usd=round(estimated_monthly_cost, 2)
    )


@router.post("/trigger-analysis/{user_id}")
async def trigger_user_analysis(
    user_id: str,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Manually trigger writing style analysis for a specific user.

    Useful for testing or re-analyzing problematic profiles.
    """
    from app.workers.tasks.ai_learning import analyze_user_writing_style_task

    # Verify user exists
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return {"success": False, "error": "User not found"}

    # Queue task
    task = analyze_user_writing_style_task.delay(user_id)

    logger.info(f"Admin {current_user.id} triggered analysis for user {user_id}, task {task.id}")

    return {
        "success": True,
        "message": f"Analysis queued for user {user.email}",
        "task_id": task.id,
        "user_email": user.email
    }


@router.post("/trigger-bulk-analysis")
async def trigger_bulk_analysis(
    only_missing: bool = True,
    current_user: User = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger analysis for multiple users.

    Args:
        only_missing: If True, only analyze users without profiles
    """
    from app.workers.tasks.ai_learning import analyze_user_writing_style_task

    # Find users needing analysis
    query = (
        select(User.id, User.email)
        .where(
            and_(
                User.email_provider.isnot(None),
                User.writing_style_profile.is_(None) if only_missing else True
            )
        )
        .limit(100)  # Safety limit
    )

    result = await db.execute(query)
    users = result.all()

    task_ids = []
    for user_id, user_email in users:
        task = analyze_user_writing_style_task.delay(str(user_id))
        task_ids.append(task.id)

    logger.info(f"Admin {current_user.id} triggered bulk analysis for {len(users)} users")

    return {
        "success": True,
        "message": f"Queued analysis for {len(users)} users",
        "task_count": len(task_ids),
        "task_ids": task_ids[:10]  # Return first 10
    }
