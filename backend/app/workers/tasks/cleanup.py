"""Cleanup tasks for database maintenance."""

import logging
from datetime import datetime, timedelta
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.models.magic_link import MagicLink
from app.models.agent_action import AgentAction, ActionStatus

logger = logging.getLogger(__name__)


@celery_app.task
def cleanup_magic_links():
    """
    Delete expired and used magic links from the database.

    This task removes magic links that have either expired or been used,
    keeping the database clean and secure.
    """
    import asyncio

    async def _cleanup():
        async with AsyncSessionLocal() as db:
            try:
                now = datetime.utcnow()

                # Delete expired magic links
                expired_result = await db.execute(
                    delete(MagicLink).where(MagicLink.expires_at < now)
                )
                expired_count = expired_result.rowcount

                # Delete used magic links older than 7 days
                week_ago = now - timedelta(days=7)
                used_result = await db.execute(
                    delete(MagicLink).where(
                        MagicLink.used_at.isnot(None),
                        MagicLink.used_at < week_ago
                    )
                )
                used_count = used_result.rowcount

                await db.commit()

                total_deleted = expired_count + used_count
                logger.info(
                    f"Cleaned up {total_deleted} magic links "
                    f"({expired_count} expired, {used_count} old used)"
                )

            except Exception as e:
                logger.error(f"Error cleaning up magic links: {str(e)}")
                await db.rollback()
                raise

    try:
        asyncio.run(_cleanup())
    except Exception as exc:
        logger.error(f"cleanup_magic_links failed: {str(exc)}")
        raise


@celery_app.task
def cleanup_old_actions():
    """
    Archive old completed agent actions.

    This task removes agent actions that have been resolved for more
    than 90 days to keep the database performant.
    """
    import asyncio

    async def _cleanup():
        async with AsyncSessionLocal() as db:
            try:
                # Delete resolved actions older than 90 days
                cutoff_date = datetime.utcnow() - timedelta(days=90)

                result = await db.execute(
                    delete(AgentAction).where(
                        AgentAction.resolved_at.isnot(None),
                        AgentAction.resolved_at < cutoff_date,
                        AgentAction.status.in_([
                            ActionStatus.APPROVED,
                            ActionStatus.REJECTED,
                            ActionStatus.EDITED
                        ])
                    )
                )

                deleted_count = result.rowcount
                await db.commit()

                logger.info(f"Archived {deleted_count} old agent actions")

            except Exception as e:
                logger.error(f"Error cleaning up old actions: {str(e)}")
                await db.rollback()
                raise

    try:
        asyncio.run(_cleanup())
    except Exception as exc:
        logger.error(f"cleanup_old_actions failed: {str(exc)}")
        raise
