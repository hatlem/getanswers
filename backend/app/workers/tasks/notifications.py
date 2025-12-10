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

                # TODO: Implement email sending
                # from app.services.email_service import EmailService
                # email_service = EmailService()
                # await email_service.send_action_notification(user, action)

                logger.info(f"Sent action notification to user {user_id} for action {action_id}")

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

                # TODO: Implement digest compilation and sending
                # from app.services.email_service import EmailService
                # from app.services.digest_service import DigestService
                # digest_service = DigestService(db)
                # digest_data = await digest_service.compile_daily_digest(user)
                # email_service = EmailService()
                # await email_service.send_daily_digest(user, digest_data)

                logger.info(f"Sent daily digest to user {user_id}")

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
