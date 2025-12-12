"""Conversation API endpoints for viewing email threads."""
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from datetime import datetime

from app.core.database import get_db
from app.core.exceptions import NotFoundError, AuthorizationError
from app.core.logging import logger
from app.api.deps import get_current_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message, MessageDirection
from app.models.objective import Objective, ObjectiveStatus
from app.models.agent_action import AgentAction, ActionStatus


router = APIRouter()


# ============================================================================
# Pydantic Schemas
# ============================================================================

class ParticipantResponse(BaseModel):
    """Participant information."""
    email: str
    name: Optional[str] = None


class TimelineMessageResponse(BaseModel):
    """A message in the conversation timeline."""
    id: str
    type: str  # 'incoming', 'outgoing', 'agent_action'
    sender: str
    sender_email: str = Field(..., serialization_alias="senderEmail")
    sender_avatar: Optional[str] = Field(None, serialization_alias="senderAvatar")
    timestamp: str  # ISO format
    content: str
    full_content: Optional[str] = Field(None, serialization_alias="fullContent")
    badge: Optional[str] = None  # 'auto', 'sent', 'pending', 'new'
    is_collapsed: bool = Field(False, serialization_alias="isCollapsed")

    class Config:
        from_attributes = True


class ConversationThreadResponse(BaseModel):
    """Full conversation thread with timeline."""
    id: str
    objective_id: str = Field(..., serialization_alias="objectiveId")
    objective_title: str = Field(..., serialization_alias="objectiveTitle")
    objective_status: str = Field(..., serialization_alias="objectiveStatus")
    agent_summary: str = Field(..., serialization_alias="agentSummary")
    participants: List[ParticipantResponse]
    timeline: List[TimelineMessageResponse]
    created_at: str = Field(..., serialization_alias="createdAt")
    updated_at: str = Field(..., serialization_alias="updatedAt")

    class Config:
        from_attributes = True


# ============================================================================
# Helper Functions
# ============================================================================

def _generate_avatar_color(email: str) -> str:
    """Generate a consistent avatar color based on email."""
    hash_value = sum(ord(c) for c in email)
    colors = [
        "linear-gradient(135deg, #ef4444, #f97316)",
        "linear-gradient(135deg, #6366f1, #8b5cf6)",
        "linear-gradient(135deg, #10b981, #34d399)",
        "linear-gradient(135deg, #f59e0b, #eab308)",
        "linear-gradient(135deg, #ec4899, #f43f5e)",
        "linear-gradient(135deg, #06b6d4, #0ea5e9)",
    ]
    return colors[hash_value % len(colors)]


def _extract_participants(conversation: Conversation, messages: List[Message]) -> List[ParticipantResponse]:
    """Extract unique participants from conversation."""
    participants_dict = {}

    for msg in messages:
        if msg.sender_email not in participants_dict:
            participants_dict[msg.sender_email] = ParticipantResponse(
                email=msg.sender_email,
                name=msg.sender_name if msg.sender_name else None,
            )

    return list(participants_dict.values())


def _build_timeline(
    conversation: Conversation,
    messages: List[Message],
    agent_actions: List[AgentAction],
) -> List[TimelineMessageResponse]:
    """Build a unified timeline from messages and agent actions."""
    timeline_items = []

    # Add all messages
    for msg in messages:
        item_type = "incoming" if msg.direction == MessageDirection.INCOMING else "outgoing"
        badge = None

        if msg.direction == MessageDirection.INCOMING:
            badge = "new"
        elif msg.direction == MessageDirection.OUTGOING:
            badge = "sent"

        timeline_items.append(TimelineMessageResponse(
            id=str(msg.id),
            type=item_type,
            sender=msg.sender_name,
            sender_email=msg.sender_email,
            sender_avatar=_generate_avatar_color(msg.sender_email),
            timestamp=msg.sent_at.isoformat(),
            content=msg.body_text[:200] + "..." if len(msg.body_text) > 200 else msg.body_text,
            full_content=msg.body_text,
            badge=badge,
            is_collapsed=len(msg.body_text) > 200,
        ))

    # Add agent actions
    for action in agent_actions:
        badge = None
        content = action.proposed_content

        if action.status == ActionStatus.PENDING:
            badge = "pending"
        elif action.status in [ActionStatus.APPROVED, ActionStatus.EDITED]:
            badge = "auto"

        # Use edited content if available
        if action.user_edit:
            content = action.user_edit

        timeline_items.append(TimelineMessageResponse(
            id=str(action.id),
            type="agent_action",
            sender="AI Assistant",
            sender_email="ai@getanswers.co",
            sender_avatar="linear-gradient(135deg, #8b5cf6, #ec4899)",
            timestamp=action.created_at.isoformat(),
            content=content[:200] + "..." if len(content) > 200 else content,
            full_content=content,
            badge=badge,
            is_collapsed=len(content) > 200,
        ))

    # Sort timeline by timestamp
    timeline_items.sort(key=lambda x: x.timestamp)

    return timeline_items


def _generate_summary(conversation: Conversation, messages: List[Message]) -> str:
    """Generate a summary of the conversation."""
    if not messages:
        return "No messages in conversation"

    # Get the first message for context
    first_msg = messages[0]
    num_messages = len(messages)

    summary = f"Email thread: {first_msg.subject}"
    if num_messages > 1:
        summary += f" ({num_messages} messages)"

    return summary


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/{conversation_id}", response_model=ConversationThreadResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get a full conversation thread with all messages and agent actions.

    Returns:
    - Conversation metadata (objective, status, etc.)
    - All messages in chronological order
    - All agent actions/proposals
    - Unified timeline combining messages and actions
    """
    logger.debug(f"Fetching conversation {conversation_id} for user {current_user.id}")

    # Fetch the conversation with all related data
    query = (
        select(Conversation)
        .options(
            joinedload(Conversation.objective),
            joinedload(Conversation.messages),
            joinedload(Conversation.agent_actions),
        )
        .where(Conversation.id == conversation_id)
    )

    result = await db.execute(query)
    conversation = result.unique().scalar_one_or_none()

    if not conversation:
        logger.warning(f"Conversation not found: {conversation_id}")
        raise NotFoundError("Conversation", str(conversation_id))

    # Verify ownership
    if conversation.objective.user_id != current_user.id:
        logger.warning(
            f"User {current_user.id} attempted to access conversation {conversation_id} "
            f"owned by {conversation.objective.user_id}"
        )
        raise AuthorizationError("You don't have permission to view this conversation")

    # Extract data
    objective = conversation.objective
    messages = sorted(conversation.messages, key=lambda m: m.sent_at)
    agent_actions = sorted(conversation.agent_actions, key=lambda a: a.created_at)

    # Build response
    participants = _extract_participants(conversation, messages)
    timeline = _build_timeline(conversation, messages, agent_actions)
    summary = _generate_summary(conversation, messages)

    logger.info(
        f"Conversation {conversation_id} fetched for user {current_user.id}: "
        f"{len(messages)} messages, {len(agent_actions)} actions"
    )

    return ConversationThreadResponse(
        id=str(conversation.id),
        objective_id=str(objective.id),
        objective_title=objective.title,
        objective_status=objective.status.value,
        agent_summary=summary,
        participants=participants,
        timeline=timeline,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat(),
    )
