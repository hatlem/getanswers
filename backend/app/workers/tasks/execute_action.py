"""Action execution tasks for sending approved emails."""

import logging
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from app.workers.celery import celery_app
from app.core.database import AsyncSessionLocal
from app.models.agent_action import AgentAction
from app.models.conversation import Conversation

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def execute_approved_action(self, action_id: str):
    """
    Execute an approved action by sending the email via Gmail.

    This task is called after an action is approved or edited.
    It uses the TriageService to execute the action which handles
    sending via Gmail API.

    Args:
        action_id: UUID string of the action to execute

    Raises:
        Exception: Re-raises exceptions after retries exhausted
    """
    import asyncio

    async def _execute():
        async with AsyncSessionLocal() as db:
            try:
                # Get action with relationships
                result = await db.execute(
                    select(AgentAction)
                    .options(
                        joinedload(AgentAction.conversation)
                        .joinedload(Conversation.objective)
                    )
                    .where(AgentAction.id == UUID(action_id))
                )
                action = result.unique().scalar_one_or_none()

                if not action:
                    logger.error(f"Action {action_id} not found")
                    return

                # Get user for Gmail credentials
                user = action.conversation.objective.user

                if not user.gmail_credentials:
                    logger.error(f"User {user.id} has no Gmail credentials for action {action_id}")
                    return

                # Initialize services
                from app.services.gmail import GmailService
                from app.services.agent import AgentService
                from app.services.triage import TriageService

                gmail_service = GmailService()
                agent_service = AgentService()
                triage_service = TriageService(db, gmail_service, agent_service)

                # Execute the action
                result = await triage_service.execute_action(action.id)

                if result.success:
                    logger.info(
                        f"Successfully executed action {action_id}: "
                        f"gmail_msg_id={result.gmail_message_id}"
                    )
                else:
                    logger.error(f"Failed to execute action {action_id}: {result.error}")
                    raise Exception(result.error)

            except Exception as e:
                logger.error(f"Error executing action {action_id}: {str(e)}")
                await db.rollback()
                raise

    try:
        asyncio.run(_execute())
    except Exception as exc:
        logger.warning(
            f"Execution failed for action {action_id}, "
            f"retrying... (attempt {self.request.retries + 1}/3)"
        )
        raise self.retry(exc=exc, countdown=30 * (2 ** self.request.retries))
