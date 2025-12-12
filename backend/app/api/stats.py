"""Stats API endpoints for dashboard metrics."""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.logging import logger
from app.api.deps import get_current_user
from app.models.user import User
from app.models.agent_action import AgentAction, ActionStatus, RiskLevel
from app.models.conversation import Conversation
from app.models.message import Message, MessageDirection
from app.models.objective import Objective, ObjectiveStatus


router = APIRouter()


# ============================================================================
# Pydantic Schemas
# ============================================================================

class NavigationCountsResponse(BaseModel):
    """Navigation counts for different status buckets."""
    needs_decision: int = Field(..., serialization_alias="needsDecision")
    waiting_on_others: int = Field(..., serialization_alias="waitingOnOthers")
    handled_by_ai: int = Field(..., serialization_alias="handledByAI")
    scheduled_done: int = Field(..., serialization_alias="scheduledDone")
    muted: int


class EfficiencyStatsResponse(BaseModel):
    """Efficiency statistics for the dashboard."""
    handled_autonomously: int = Field(..., serialization_alias="handledAutonomously")
    total_today: int = Field(..., serialization_alias="totalToday")
    percentage: float  # percentage


class GlobalStatusResponse(BaseModel):
    """Global status for the mission control header."""
    status: str  # 'all_clear', 'pending_decisions', 'urgent'
    message: str
    pending_count: int = Field(..., serialization_alias="pendingCount")


class StatsResponse(BaseModel):
    """Complete stats response for the dashboard."""
    navigation_counts: NavigationCountsResponse = Field(..., serialization_alias="navigationCounts")
    efficiency_stats: EfficiencyStatsResponse = Field(..., serialization_alias="efficiencyStats")
    global_status: GlobalStatusResponse = Field(..., serialization_alias="globalStatus")


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comprehensive statistics for the dashboard.

    Returns:
    - navigationCounts: Counts for each status bucket in the navigation
    - efficiencyStats: Time saved, emails processed, and automation rate
    - globalStatus: Overall system status and pending count
    """
    logger.debug(f"Fetching stats for user {current_user.id}")

    # ========================================================================
    # Navigation Counts
    # ========================================================================

    # Needs decision (pending actions)
    needs_decision_query = (
        select(func.count(AgentAction.id))
        .join(AgentAction.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                AgentAction.status == ActionStatus.PENDING
            )
        )
    )
    result = await db.execute(needs_decision_query)
    needs_decision = result.scalar() or 0

    # Waiting on others
    waiting_on_others_query = (
        select(func.count(Objective.id))
        .where(
            and_(
                Objective.user_id == current_user.id,
                Objective.status == ObjectiveStatus.WAITING_ON_OTHERS
            )
        )
    )
    result = await db.execute(waiting_on_others_query)
    waiting_on_others = result.scalar() or 0

    # Handled by AI
    handled_by_ai_query = (
        select(func.count(AgentAction.id))
        .join(AgentAction.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                or_(
                    AgentAction.status == ActionStatus.APPROVED,
                    AgentAction.status == ActionStatus.EDITED
                )
            )
        )
    )
    result = await db.execute(handled_by_ai_query)
    handled_by_ai = result.scalar() or 0

    # Scheduled/Done
    scheduled_done_query = (
        select(func.count(Objective.id))
        .where(
            and_(
                Objective.user_id == current_user.id,
                Objective.status == ObjectiveStatus.SCHEDULED
            )
        )
    )
    result = await db.execute(scheduled_done_query)
    scheduled_done = result.scalar() or 0

    # Muted
    muted_query = (
        select(func.count(Objective.id))
        .where(
            and_(
                Objective.user_id == current_user.id,
                Objective.status == ObjectiveStatus.MUTED
            )
        )
    )
    result = await db.execute(muted_query)
    muted = result.scalar() or 0

    # ========================================================================
    # Efficiency Stats (today)
    # ========================================================================

    # Get start of today (midnight UTC)
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Total emails today (incoming messages)
    total_today_query = (
        select(func.count(Message.id))
        .join(Message.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                Message.direction == MessageDirection.INCOMING,
                Message.created_at >= today_start
            )
        )
    )
    result = await db.execute(total_today_query)
    total_today = result.scalar() or 0

    # Emails handled autonomously today
    handled_autonomously_query = (
        select(func.count(AgentAction.id))
        .join(AgentAction.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                or_(
                    AgentAction.status == ActionStatus.APPROVED,
                    AgentAction.status == ActionStatus.EDITED
                ),
                AgentAction.created_at >= today_start
            )
        )
    )
    result = await db.execute(handled_autonomously_query)
    handled_autonomously = result.scalar() or 0

    # Calculate automation percentage
    percentage = 0.0
    if total_today > 0:
        percentage = (handled_autonomously / total_today) * 100

    # ========================================================================
    # Global Status
    # ========================================================================

    # Determine status based on pending count and risk
    if needs_decision == 0:
        status = "all_clear"
        message = "All caught up! No pending decisions."
    elif needs_decision > 10:
        status = "urgent"
        message = f"{needs_decision} items need your attention"
    else:
        status = "pending_decisions"
        message = f"{needs_decision} item{'s' if needs_decision != 1 else ''} pending review"

    # Check for high-risk pending items
    high_risk_query = (
        select(func.count(AgentAction.id))
        .join(AgentAction.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                AgentAction.status == ActionStatus.PENDING,
                AgentAction.risk_level == RiskLevel.HIGH
            )
        )
    )
    result = await db.execute(high_risk_query)
    high_risk_count = result.scalar() or 0

    if high_risk_count > 0:
        status = "urgent"
        message = f"{high_risk_count} high-priority item{'s' if high_risk_count != 1 else ''} need attention"

    logger.info(f"Stats fetched for user {current_user.id}: {needs_decision} pending, {percentage:.1f}% automation")

    return StatsResponse(
        navigation_counts=NavigationCountsResponse(
            needs_decision=needs_decision,
            waiting_on_others=waiting_on_others,
            handled_by_ai=handled_by_ai,
            scheduled_done=scheduled_done,
            muted=muted,
        ),
        efficiency_stats=EfficiencyStatsResponse(
            handled_autonomously=handled_autonomously,
            total_today=total_today,
            percentage=round(percentage, 1),
        ),
        global_status=GlobalStatusResponse(
            status=status,
            message=message,
            pending_count=needs_decision,
        ),
    )
