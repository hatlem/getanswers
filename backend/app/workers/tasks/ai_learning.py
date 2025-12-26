"""Background tasks for AI learning - Writing style and edit pattern analysis.

These tasks run periodically to:
- Analyze user writing styles from sent emails
- Identify edit patterns
- Update writing style profiles automatically
- Ensure AI stays current with user preferences
"""

from datetime import datetime, timedelta
from uuid import UUID
import asyncio

from celery import Task
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery import celery_app
from app.core.database import async_session
from app.core.config import settings
from app.core.logging import logger
from app.models.user import User
from app.models.agent_action import AgentAction, ActionStatus
from app.models.conversation import Conversation
from app.models.objective import Objective
from app.services.writing_style import WritingStyleService
from app.services.edit_learning import EditLearningService


# =============================================================================
# Writing Style Analysis Tasks
# =============================================================================

@celery_app.task(
    name="analyze_user_writing_style",
    bind=True,
    max_retries=3,
    default_retry_delay=300  # 5 minutes
)
def analyze_user_writing_style_task(self: Task, user_id: str) -> dict:
    """
    Analyze a user's writing style from their sent emails.

    This task:
    1. Fetches the user's recent sent emails
    2. Analyzes writing patterns using Claude AI
    3. Caches the profile in the database
    4. Returns analysis results

    Args:
        user_id: UUID of the user to analyze

    Returns:
        dict with analysis results and status
    """
    try:
        # Run async code in sync context
        result = asyncio.run(_analyze_user_writing_style(UUID(user_id)))

        logger.info(
            f"Writing style analysis completed for user {user_id}: "
            f"{result['sample_size']} emails analyzed"
        )

        return result

    except Exception as e:
        logger.error(f"Failed to analyze writing style for user {user_id}: {e}", exc_info=True)

        # Retry on failure (up to max_retries)
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)

        return {
            "success": False,
            "error": str(e),
            "user_id": user_id
        }


async def _analyze_user_writing_style(user_id: UUID) -> dict:
    """Async implementation of writing style analysis."""
    async with async_session() as db:
        # Get user
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User {user_id} not found")

        # Check if API key is configured
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic API key not configured")

        # Initialize service
        writing_service = WritingStyleService(api_key=settings.ANTHROPIC_API_KEY)

        # Analyze writing style
        analysis_result = await writing_service.analyze_user_writing_style(
            db=db,
            user_id=user_id,
            lookback_days=90,
            max_emails=50
        )

        # Cache the profile
        user.writing_style_profile = analysis_result.profile.model_dump_json()
        await db.commit()

        return {
            "success": True,
            "user_id": str(user_id),
            "sample_size": analysis_result.profile.sample_size,
            "confidence": analysis_result.profile.confidence,
            "insights": analysis_result.insights,
            "recommendations": analysis_result.recommendations
        }


# =============================================================================
# Edit Pattern Analysis Tasks
# =============================================================================

@celery_app.task(
    name="analyze_user_edit_patterns",
    bind=True,
    max_retries=3,
    default_retry_delay=300
)
def analyze_user_edit_patterns_task(self: Task, user_id: str) -> dict:
    """
    Analyze a user's edit patterns to improve future AI responses.

    This task:
    1. Fetches the user's recent edits
    2. Identifies patterns in how they modify AI responses
    3. Updates writing style profile based on edit patterns
    4. Returns analysis results

    Args:
        user_id: UUID of the user to analyze

    Returns:
        dict with analysis results and status
    """
    try:
        result = asyncio.run(_analyze_user_edit_patterns(UUID(user_id)))

        if result['success']:
            logger.info(
                f"Edit pattern analysis completed for user {user_id}: "
                f"{result.get('sample_size', 0)} edits analyzed"
            )
        else:
            logger.info(f"Insufficient edit data for user {user_id}")

        return result

    except Exception as e:
        logger.error(f"Failed to analyze edit patterns for user {user_id}: {e}", exc_info=True)

        if self.request.retries < self.max_retries:
            raise self.retry(exc=e)

        return {
            "success": False,
            "error": str(e),
            "user_id": user_id
        }


async def _analyze_user_edit_patterns(user_id: UUID) -> dict:
    """Async implementation of edit pattern analysis."""
    async with async_session() as db:
        # Get user
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User {user_id} not found")

        # Check if API key is configured
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("Anthropic API key not configured")

        # Initialize service
        edit_service = EditLearningService(api_key=settings.ANTHROPIC_API_KEY)

        # Analyze edit patterns
        analysis = await edit_service.analyze_user_edit_patterns(
            db=db,
            user_id=user_id,
            lookback_days=30,
            min_edits=5
        )

        if not analysis:
            return {
                "success": False,
                "user_id": str(user_id),
                "reason": "Insufficient edit data (need at least 5 edits)"
            }

        # Update writing style profile if we have one
        if user.writing_style_profile:
            await edit_service.update_writing_style_from_edits(
                db=db,
                user=user,
                edit_analysis=analysis
            )

        return {
            "success": True,
            "user_id": str(user_id),
            "sample_size": analysis.sample_size,
            "avg_edit_percentage": analysis.avg_edit_percentage,
            "heavy_edit_rate": analysis.heavy_edit_rate,
            "patterns_found": len(analysis.patterns),
            "recommendations": analysis.recommendations
        }


# =============================================================================
# Automated Learning Tasks (Periodic)
# =============================================================================

@celery_app.task(name="refresh_stale_writing_profiles")
def refresh_stale_writing_profiles_task() -> dict:
    """
    Refresh writing style profiles that are older than 30 days.

    This task runs periodically (e.g., daily) to:
    1. Find users with stale writing profiles (>30 days old)
    2. Queue analysis tasks for each user
    3. Return statistics

    Returns:
        dict with refresh statistics
    """
    try:
        result = asyncio.run(_refresh_stale_writing_profiles())

        logger.info(
            f"Writing profile refresh completed: {result['profiles_refreshed']} profiles queued"
        )

        return result

    except Exception as e:
        logger.error(f"Failed to refresh stale writing profiles: {e}", exc_info=True)

        return {
            "success": False,
            "error": str(e),
            "profiles_refreshed": 0
        }


async def _refresh_stale_writing_profiles() -> dict:
    """Async implementation of profile refresh."""
    async with async_session() as db:
        # Find users with stale profiles (>30 days old) or no profile
        import json

        query = select(User).where(
            and_(
                User.writing_style_profile.isnot(None),
                User.email_provider.isnot(None)  # Must have email connected
            )
        )

        result = await db.execute(query)
        users = result.scalars().all()

        profiles_refreshed = 0
        cutoff_date = datetime.utcnow() - timedelta(days=30)

        for user in users:
            try:
                profile_data = json.loads(user.writing_style_profile)
                last_updated = profile_data.get("last_updated")

                if last_updated:
                    last_updated_dt = datetime.fromisoformat(last_updated)

                    # Refresh if stale
                    if last_updated_dt < cutoff_date:
                        logger.info(f"Queuing writing style refresh for user {user.id}")
                        analyze_user_writing_style_task.delay(str(user.id))
                        profiles_refreshed += 1

            except Exception as e:
                logger.warning(f"Failed to check profile freshness for user {user.id}: {e}")
                continue

        return {
            "success": True,
            "profiles_checked": len(users),
            "profiles_refreshed": profiles_refreshed
        }


@celery_app.task(name="auto_analyze_new_edits")
def auto_analyze_new_edits_task() -> dict:
    """
    Automatically analyze edit patterns for users with recent edits.

    This task runs periodically (e.g., weekly) to:
    1. Find users who have made edits in the last 7 days
    2. Queue edit pattern analysis for users with enough edits (5+)
    3. Return statistics

    Returns:
        dict with analysis statistics
    """
    try:
        result = asyncio.run(_auto_analyze_new_edits())

        logger.info(
            f"Auto edit analysis completed: {result['analyses_queued']} analyses queued"
        )

        return result

    except Exception as e:
        logger.error(f"Failed to auto-analyze new edits: {e}", exc_info=True)

        return {
            "success": False,
            "error": str(e),
            "analyses_queued": 0
        }


async def _auto_analyze_new_edits() -> dict:
    """Async implementation of auto edit analysis."""
    async with async_session() as db:
        # Find users with recent edits (last 7 days)
        time_threshold = datetime.utcnow() - timedelta(days=7)

        # Count edits per user in last 7 days
        query = (
            select(Objective.user_id, func.count(AgentAction.id).label('edit_count'))
            .join(Conversation, Conversation.objective_id == Objective.id)
            .join(AgentAction, AgentAction.conversation_id == Conversation.id)
            .where(
                and_(
                    AgentAction.status == ActionStatus.EDITED,
                    AgentAction.user_edit.isnot(None),
                    AgentAction.approved_at >= time_threshold
                )
            )
            .group_by(Objective.user_id)
            .having(func.count(AgentAction.id) >= 5)  # Need at least 5 edits
        )

        result = await db.execute(query)
        user_edit_counts = result.all()

        analyses_queued = 0

        for user_id, edit_count in user_edit_counts:
            logger.info(f"Queuing edit pattern analysis for user {user_id} ({edit_count} edits)")
            analyze_user_edit_patterns_task.delay(str(user_id))
            analyses_queued += 1

        return {
            "success": True,
            "users_checked": len(user_edit_counts),
            "analyses_queued": analyses_queued
        }


# =============================================================================
# Initial Analysis for New Users
# =============================================================================

@celery_app.task(name="initial_writing_analysis_for_new_user")
def initial_writing_analysis_for_new_user_task(user_id: str) -> dict:
    """
    Trigger initial writing style analysis for a new user after onboarding.

    This task should be called when:
    1. User completes onboarding
    2. User sends their first few emails through GetAnswers

    Args:
        user_id: UUID of the user

    Returns:
        dict with analysis results
    """
    try:
        result = asyncio.run(_initial_writing_analysis(UUID(user_id)))

        logger.info(f"Initial writing analysis for user {user_id}: {result}")

        return result

    except Exception as e:
        logger.error(f"Failed initial writing analysis for user {user_id}: {e}", exc_info=True)

        return {
            "success": False,
            "error": str(e),
            "user_id": user_id
        }


async def _initial_writing_analysis(user_id: UUID) -> dict:
    """Async implementation of initial analysis."""
    async with async_session() as db:
        # Get user
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError(f"User {user_id} not found")

        # Check if already has profile
        if user.writing_style_profile:
            return {
                "success": True,
                "user_id": str(user_id),
                "message": "User already has writing profile",
                "skipped": True
            }

        # Check if user has sent any emails
        from app.models.message import Message, MessageDirection

        sent_count_query = (
            select(func.count(Message.id))
            .join(Message.conversation)
            .join(Conversation.objective)
            .where(
                and_(
                    Objective.user_id == user_id,
                    Message.direction == MessageDirection.OUTGOING
                )
            )
        )

        count_result = await db.execute(sent_count_query)
        sent_count = count_result.scalar() or 0

        if sent_count < 3:
            return {
                "success": True,
                "user_id": str(user_id),
                "message": f"Insufficient sent emails ({sent_count}/3 minimum)",
                "skipped": True
            }

        # Queue analysis task
        analyze_user_writing_style_task.delay(str(user_id))

        return {
            "success": True,
            "user_id": str(user_id),
            "message": "Writing style analysis queued",
            "sent_emails": sent_count
        }
