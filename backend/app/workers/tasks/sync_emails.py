"""Email synchronization tasks."""

import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def sync_user_emails(self, user_id: str):
    """
    Sync emails for a single user.

    This task fetches new emails from Gmail for a specific user
    and processes them through the AI triage system.

    Args:
        user_id: UUID string of the user to sync

    Raises:
        Exception: Re-raises exceptions after retries exhausted
    """
    import asyncio

    async def _sync():
        async with AsyncSessionLocal() as db:
            try:
                # Get user with Gmail credentials
                result = await db.execute(
                    select(User).where(User.id == UUID(user_id))
                )
                user = result.scalar_one_or_none()

                if not user:
                    logger.error(f"User {user_id} not found")
                    return

                if not user.gmail_credentials:
                    logger.warning(f"User {user_id} has no Gmail credentials")
                    return

                # Initialize services and sync inbox
                from app.services.gmail import GmailService
                from app.services.agent import AgentService
                from app.services.triage import TriageService

                gmail_service = GmailService()
                agent_service = AgentService()
                triage_service = TriageService(db, gmail_service, agent_service)

                result = await triage_service.sync_user_inbox(user.id)
                logger.info(
                    f"Successfully synced emails for user {user_id}: "
                    f"{result.processed}/{result.new_messages} processed, {result.errors} errors"
                )

            except Exception as e:
                logger.error(f"Error syncing emails for user {user_id}: {str(e)}")
                await db.rollback()
                raise

    try:
        asyncio.run(_sync())
    except Exception as exc:
        logger.warning(f"Sync failed for user {user_id}, retrying... (attempt {self.request.retries + 1}/3)")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task
def sync_all_users():
    """
    Periodic task to sync all users with connected Gmail accounts.

    This task queries all users who have Gmail credentials configured
    and dispatches individual sync tasks for each user.
    """
    import asyncio

    async def _sync_all():
        async with AsyncSessionLocal() as db:
            try:
                # Get all users with Gmail credentials
                result = await db.execute(
                    select(User).where(User.gmail_credentials.isnot(None))
                )
                users = result.scalars().all()

                logger.info(f"Found {len(users)} users with Gmail connected")

                # Dispatch sync task for each user
                for user in users:
                    sync_user_emails.delay(str(user.id))
                    logger.debug(f"Dispatched sync task for user {user.id}")

            except Exception as e:
                logger.error(f"Error querying users for sync: {str(e)}")
                await db.rollback()
                raise

    try:
        asyncio.run(_sync_all())
    except Exception as exc:
        logger.error(f"sync_all_users failed: {str(exc)}")
        raise
