"""Email processing tasks for AI triage."""

import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.models.message import Message

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_single_email(self, message_id: str):
    """
    Process a single email through the AI triage pipeline.

    This task takes an email message and runs it through Claude AI
    to determine priority, categorization, and suggested actions.

    Args:
        message_id: UUID string of the message to process

    Raises:
        Exception: Re-raises exceptions after retries exhausted
    """
    import asyncio

    async def _process():
        async with AsyncSessionLocal() as db:
            try:
                # Get message
                result = await db.execute(
                    select(Message).where(Message.id == UUID(message_id))
                )
                message = result.scalar_one_or_none()

                if not message:
                    logger.error(f"Message {message_id} not found")
                    return

                # TODO: Implement AI processing through TriageService
                # from app.services.triage_service import TriageService
                # triage_service = TriageService(db)
                # await triage_service.process_message(message)

                logger.info(f"Successfully processed message {message_id}")

            except Exception as e:
                logger.error(f"Error processing message {message_id}: {str(e)}")
                await db.rollback()
                raise

    try:
        asyncio.run(_process())
    except Exception as exc:
        logger.warning(
            f"Processing failed for message {message_id}, "
            f"retrying... (attempt {self.request.retries + 1}/3)"
        )
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))


@celery_app.task
def batch_process_emails(message_ids: list[str]):
    """
    Process multiple emails in batch (useful for initial sync).

    This task takes a list of message IDs and dispatches individual
    processing tasks for each, allowing for parallel processing.

    Args:
        message_ids: List of message UUID strings to process
    """
    logger.info(f"Dispatching batch processing for {len(message_ids)} messages")

    # Dispatch individual processing tasks
    for message_id in message_ids:
        process_single_email.delay(message_id)
        logger.debug(f"Dispatched processing task for message {message_id}")

    logger.info(f"Successfully dispatched {len(message_ids)} processing tasks")
