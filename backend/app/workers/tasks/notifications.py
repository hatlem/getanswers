"""Notification tasks for user alerts and digests."""

import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.agent_action import AgentAction, ActionStatus, RiskLevel

logger = logging.getLogger(__name__)


@celery_app.task
def send_action_notification(user_id: str, action_id: str):
    """
    Send notification for a high-risk pending action.

    This task sends an email notification to the user when a high-risk
    action requires their review and approval.

    Args:
        user_id: UUID string of the user to notify
        action_id: UUID string of the action requiring attention
    """
    import asyncio

    async def _send():
        async with AsyncSessionLocal() as db:
            try:
                # Get user
                result = await db.execute(
                    select(User).where(User.id == UUID(user_id))
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User {user_id} not found")
                    return

                # Get action
                result = await db.execute(
                    select(AgentAction).where(AgentAction.id == UUID(action_id))
                )
                action = result.scalar_one_or_none()

                if not action:
                    logger.error(f"Action {action_id} not found")
                    return

                if action.risk_level != RiskLevel.HIGH:
                    logger.info(f"Action {action_id} is not high-risk, skipping notification")
                    return

                # Send notification email
                from app.services.email import email_service

                success = await email_service.send_action_notification(
                    to=user.email,
                    action_summary=action.proposed_content[:200] if action.proposed_content else "Action pending review",
                    action_id=str(action_id),
                    risk_level=action.risk_level.value.upper()
                )

                if success:
                    logger.info(f"Sent action notification to user {user_id} for action {action_id}")
                else:
                    logger.warning(f"Failed to send action notification to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending action notification: {str(e)}")
                await db.rollback()
                raise

    try:
        asyncio.run(_send())
    except Exception as exc:
        logger.error(f"send_action_notification failed: {str(exc)}")
        raise


@celery_app.task
def send_daily_digest(user_id: str):
    """
    Send daily activity digest to a user.

    This task compiles a summary of the day's email activity,
    pending actions, and AI triage results.

    Args:
        user_id: UUID string of the user to send digest to
    """
    import asyncio

    async def _send():
        async with AsyncSessionLocal() as db:
            try:
                # Get user
                result = await db.execute(
                    select(User).where(User.id == UUID(user_id))
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User {user_id} not found")
                    return

                # Get stats for user
                from datetime import datetime, timedelta
                from sqlalchemy import func, and_, or_
                from app.models.agent_action import AgentAction, ActionStatus
                from app.models.conversation import Conversation
                from app.models.objective import Objective

                time_window = datetime.utcnow() - timedelta(days=1)

                # Count emails processed today
                processed_query = (
                    select(func.count(AgentAction.id))
                    .join(AgentAction.conversation)
                    .join(Conversation.objective)
                    .where(
                        and_(
                            Objective.user_id == UUID(user_id),
                            AgentAction.created_at >= time_window
                        )
                    )
                )
                result = await db.execute(processed_query)
                emails_processed = result.scalar() or 0

                # Count responses sent
                sent_query = (
                    select(func.count(AgentAction.id))
                    .join(AgentAction.conversation)
                    .join(Conversation.objective)
                    .where(
                        and_(
                            Objective.user_id == UUID(user_id),
                            AgentAction.created_at >= time_window,
                            or_(
                                AgentAction.status == ActionStatus.APPROVED,
                                AgentAction.status == ActionStatus.EDITED
                            )
                        )
                    )
                )
                result = await db.execute(sent_query)
                responses_sent = result.scalar() or 0

                # Get pending actions
                pending_query = (
                    select(AgentAction)
                    .join(AgentAction.conversation)
                    .join(Conversation.objective)
                    .where(
                        and_(
                            Objective.user_id == UUID(user_id),
                            AgentAction.status == ActionStatus.PENDING
                        )
                    )
                    .limit(10)
                )
                result = await db.execute(pending_query)
                pending_actions = result.scalars().all()

                stats = {
                    'emails_processed': emails_processed,
                    'responses_sent': responses_sent,
                    'time_saved_minutes': responses_sent * 5  # Estimate 5 min saved per response
                }

                pending_list = [
                    {'summary': action.proposed_content[:100] if action.proposed_content else 'Action pending'}
                    for action in pending_actions
                ]

                # Send digest email
                from app.services.email import email_service

                success = await email_service.send_daily_digest(
                    to=user.email,
                    stats=stats,
                    pending_actions=pending_list
                )

                if success:
                    logger.info(f"Sent daily digest to user {user_id}")
                else:
                    logger.warning(f"Failed to send daily digest to user {user_id}")

            except Exception as e:
                logger.error(f"Error sending daily digest to user {user_id}: {str(e)}")
                await db.rollback()
                raise

    try:
        asyncio.run(_send())
    except Exception as exc:
        logger.error(f"send_daily_digest failed: {str(exc)}")
        raise


@celery_app.task
def send_daily_digests_all():
    """
    Periodic task to send daily digests to all active users.

    This task queries all users and dispatches individual digest
    tasks for each user.
    """
    import asyncio

    async def _send_all():
        async with AsyncSessionLocal() as db:
            try:
                # Get all users
                result = await db.execute(select(User))
                users = result.scalars().all()

                logger.info(f"Dispatching daily digests for {len(users)} users")

                # Dispatch digest task for each user
                for user in users:
                    send_daily_digest.delay(str(user.id))
                    logger.debug(f"Dispatched digest task for user {user.id}")

            except Exception as e:
                logger.error(f"Error querying users for digests: {str(e)}")
                await db.rollback()
                raise

    try:
        asyncio.run(_send_all())
    except Exception as exc:
        logger.error(f"send_daily_digests_all failed: {str(exc)}")
        raise
