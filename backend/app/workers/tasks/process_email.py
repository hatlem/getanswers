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

                # Get user for this message
                from sqlalchemy.orm import selectinload
                from app.models.conversation import Conversation
                from app.models.objective import Objective

                # Load message with conversation and objective
                result = await db.execute(
                    select(Message)
                    .options(
                        selectinload(Message.conversation)
                        .selectinload(Conversation.objective)
                    )
                    .where(Message.id == UUID(message_id))
                )
                message = result.scalar_one_or_none()

                if not message or not message.conversation or not message.conversation.objective:
                    logger.error(f"Message {message_id} has no associated objective")
                    return

                user_id = message.conversation.objective.user_id

                # Initialize services and process the email
                from app.services.gmail import GmailService
                from app.services.agent import AgentService
                from app.services.triage import TriageService

                gmail_service = GmailService()
                agent_service = AgentService()
                triage_service = TriageService(db, gmail_service, agent_service)

                # Build a gmail_message dict from our Message model
                gmail_message = {
                    'id': message.gmail_message_id,
                    'threadId': message.conversation.gmail_thread_id,
                    'from': {
                        'name': message.sender_name,
                        'email': message.sender_email
                    },
                    'subject': message.subject,
                    'body_text': message.body_text,
                    'body_html': message.body_html,
                    'sent_at': message.sent_at
                }

                result = await triage_service.process_new_email(user_id, gmail_message)
                logger.info(
                    f"Successfully processed message {message_id}: "
                    f"action_id={result.action_id}, confidence={result.confidence:.1f}"
                )

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
