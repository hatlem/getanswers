"""Queue API endpoints for reviewing and managing AI-proposed actions."""
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload, joinedload
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.exceptions import (
    NotFoundError,
    AuthorizationError,
    ValidationError,
    DatabaseError
)
from app.core.logging import logger
from app.core.audit import AuditLog
from app.api.deps import get_current_user
from app.models.user import User
from app.models.agent_action import AgentAction, ActionStatus, RiskLevel, ActionType
from app.models.conversation import Conversation
from app.models.message import Message, MessageDirection
from app.models.objective import Objective, ObjectiveStatus


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


router = APIRouter()


# ============================================================================
# Pydantic Schemas
# ============================================================================

class SenderTag(BaseModel):
    """Tag for sender categorization."""
    label: str
    type: str  # 'vip', 'key', 'new', 'blocked', 'custom'


class Sender(BaseModel):
    """Sender information."""
    id: str
    name: str
    email: str
    organization: Optional[str] = None
    avatar_url: Optional[str] = None
    avatar_color: Optional[str] = None
    tags: List[SenderTag] = []


class RelatedItem(BaseModel):
    """Related item reference (invoice, contract, etc.)."""
    id: str
    label: str
    href: str
    type: str  # 'invoice', 'contract', 'project', 'document', 'ticket'


class QueueItemResponse(BaseModel):
    """Full queue item with conversation context."""
    id: str
    objective_id: str
    priority_score: int
    risk_level: str  # 'high', 'medium', 'low'
    category: str  # 'finance', 'client', 'hr', 'legal', 'internal', 'partner'
    confidence_score: int
    summary: str
    proposed_action: str
    is_uncertain: bool = False
    sender: Sender
    related_items: List[RelatedItem] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueueResponse(BaseModel):
    """Queue list response with stats."""
    cards: List[QueueItemResponse]
    total: int
    needs_decision: int
    waiting_on_others: int
    handled_by_ai: int
    scheduled_done: int
    muted: int


class ApproveRequest(BaseModel):
    """Request body for approving an action."""
    notes: Optional[str] = Field(None, description="Optional notes about the approval")


class OverrideRequest(BaseModel):
    """Request body for overriding/rejecting an action."""
    reason: str = Field(..., description="Reason for overriding the action")


class EditRequest(BaseModel):
    """Request body for editing an action."""
    edited_content: str = Field(..., description="The edited content to send instead")


class EscalateRequest(BaseModel):
    """Request body for escalating an action."""
    reason: Optional[str] = Field(None, description="Reason for escalation")
    notify_team: bool = Field(False, description="Whether to notify team members")


class ActionResponse(BaseModel):
    """Generic action response."""
    success: bool
    message: str
    action_id: str
    action: Optional[QueueItemResponse] = None


class StatsResponse(BaseModel):
    """Statistics response."""
    total_emails: int
    handled_by_ai: int
    pending_review: int
    efficiency_rate: float
    avg_confidence: float
    avg_response_time: Optional[float] = None


# ============================================================================
# Helper Functions
# ============================================================================

def _extract_sender_from_message(message: Message) -> Sender:
    """Extract sender information from a message."""
    # Generate a simple avatar color based on email
    hash_value = sum(ord(c) for c in message.sender_email)
    colors = [
        "linear-gradient(135deg, #ef4444, #f97316)",
        "linear-gradient(135deg, #6366f1, #8b5cf6)",
        "linear-gradient(135deg, #10b981, #34d399)",
        "linear-gradient(135deg, #f59e0b, #eab308)",
        "linear-gradient(135deg, #ec4899, #f43f5e)",
        "linear-gradient(135deg, #06b6d4, #0ea5e9)",
    ]

    return Sender(
        id=f"sender-{hash_value}",
        name=message.sender_name,
        email=message.sender_email,
        organization=None,  # TODO: Extract from domain or company database
        avatar_color=colors[hash_value % len(colors)],
        tags=[],  # TODO: Implement tag system
    )


def _determine_category(conversation: Conversation, message: Message) -> str:
    """Determine the category based on message content and context."""
    # Simple keyword-based categorization
    content = (message.subject + " " + message.body_text).lower()

    if any(word in content for word in ["invoice", "payment", "bill", "cost", "budget", "financial"]):
        return "finance"
    elif any(word in content for word in ["client", "customer", "account"]):
        return "client"
    elif any(word in content for word in ["hire", "onboard", "employee", "hr", "benefits"]):
        return "hr"
    elif any(word in content for word in ["contract", "legal", "agreement", "terms"]):
        return "legal"
    elif any(word in content for word in ["partner", "vendor", "supplier"]):
        return "partner"
    else:
        return "internal"


def _generate_summary(conversation: Conversation, latest_message: Message) -> str:
    """Generate a summary of the conversation."""
    # For now, use the subject as summary
    # TODO: Use AI to generate better summaries
    return latest_message.subject[:200]


def _action_to_queue_item(
    action: AgentAction,
    conversation: Conversation,
    objective: Objective,
    latest_message: Message,
) -> QueueItemResponse:
    """Convert an AgentAction to a QueueItemResponse."""
    sender = _extract_sender_from_message(latest_message)
    category = _determine_category(conversation, latest_message)
    summary = _generate_summary(conversation, latest_message)

    # Determine if action is uncertain (low confidence)
    is_uncertain = action.confidence_score < 0.6

    return QueueItemResponse(
        id=str(action.id),
        objective_id=str(objective.id),
        priority_score=action.priority_score,
        risk_level=action.risk_level.value,
        category=category,
        confidence_score=int(action.confidence_score * 100),
        summary=summary,
        proposed_action=action.proposed_content,
        is_uncertain=is_uncertain,
        sender=sender,
        related_items=[],  # TODO: Implement related items lookup
        created_at=action.created_at,
        updated_at=conversation.updated_at,
    )


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("", response_model=QueueResponse)
async def get_review_queue(
    status: Optional[str] = Query(None, description="Filter by status: pending, approved, rejected"),
    risk: Optional[str] = Query(None, description="Filter by risk level: high, medium, low"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all items in the review queue that need user decision.

    Fetches AgentActions with their associated conversations, messages, and objectives.
    Supports filtering by status and risk level.
    """
    # Build the query with proper joins
    query = (
        select(AgentAction)
        .join(AgentAction.conversation)
        .join(Conversation.objective)
        .where(Objective.user_id == current_user.id)
        .options(
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.objective),
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.messages),
        )
    )

    # Apply status filter
    if status:
        try:
            status_enum = ActionStatus(status.lower())
            query = query.where(AgentAction.status == status_enum)
        except ValueError:
            logger.warning(f"Invalid status filter: {status}")
            raise ValidationError(f"Invalid status: {status}")
    else:
        # Default to pending items only
        query = query.where(AgentAction.status == ActionStatus.PENDING)

    # Apply risk filter
    if risk:
        try:
            risk_enum = RiskLevel(risk.lower())
            query = query.where(AgentAction.risk_level == risk_enum)
        except ValueError:
            logger.warning(f"Invalid risk filter: {risk}")
            raise ValidationError(f"Invalid risk level: {risk}")

    # Order by priority and creation time
    query = query.order_by(
        AgentAction.priority_score.desc(),
        AgentAction.created_at.desc()
    )

    # Get total count before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    actions = result.unique().scalars().all()

    # Convert to response format
    cards = []
    for action in actions:
        conversation = action.conversation
        objective = conversation.objective

        # Get the latest incoming message
        latest_message = None
        for msg in sorted(conversation.messages, key=lambda m: m.sent_at, reverse=True):
            if msg.direction == MessageDirection.INCOMING:
                latest_message = msg
                break

        if not latest_message:
            # Skip if no incoming message found
            continue

        queue_item = _action_to_queue_item(action, conversation, objective, latest_message)
        cards.append(queue_item)

    # Get stats for the user
    stats_queries = [
        # Needs decision (pending)
        select(func.count()).select_from(AgentAction)
        .join(AgentAction.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                AgentAction.status == ActionStatus.PENDING
            )
        ),
        # Waiting on others
        select(func.count()).select_from(Objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                Objective.status == ObjectiveStatus.WAITING_ON_OTHERS
            )
        ),
        # Handled by AI
        select(func.count()).select_from(AgentAction)
        .join(AgentAction.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                AgentAction.status == ActionStatus.APPROVED
            )
        ),
        # Scheduled
        select(func.count()).select_from(Objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                Objective.status == ObjectiveStatus.SCHEDULED
            )
        ),
        # Muted
        select(func.count()).select_from(Objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                Objective.status == ObjectiveStatus.MUTED
            )
        ),
    ]

    # Execute all stats queries
    stats_results = await db.execute(stats_queries[0])
    needs_decision = stats_results.scalar() or 0

    stats_results = await db.execute(stats_queries[1])
    waiting_on_others = stats_results.scalar() or 0

    stats_results = await db.execute(stats_queries[2])
    handled_by_ai = stats_results.scalar() or 0

    stats_results = await db.execute(stats_queries[3])
    scheduled_done = stats_results.scalar() or 0

    stats_results = await db.execute(stats_queries[4])
    muted = stats_results.scalar() or 0

    return QueueResponse(
        cards=cards,
        total=total,
        needs_decision=needs_decision,
        waiting_on_others=waiting_on_others,
        handled_by_ai=handled_by_ai,
        scheduled_done=scheduled_done,
        muted=muted,
    )


@router.post("/{action_id}/approve", response_model=ActionResponse)
async def approve_action(
    req: Request,
    action_id: UUID,
    request: ApproveRequest = ApproveRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve the AI's proposed action and mark it for execution.

    This will:
    1. Verify the action belongs to the current user
    2. Update the action status to 'approved'
    3. Set the approved_at timestamp
    4. Mark it ready for execution (Gmail integration will happen later)
    """
    client_ip = get_client_ip(req)

    # Fetch the action with its relationships
    query = (
        select(AgentAction)
        .options(
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.objective),
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.messages),
        )
        .where(AgentAction.id == action_id)
    )

    result = await db.execute(query)
    action = result.unique().scalar_one_or_none()

    if not action:
        logger.warning(f"Approve action: Action not found {action_id}")
        raise NotFoundError("Action", str(action_id))

    # Verify ownership
    if action.conversation.objective.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to approve action {action_id} without permission")
        await AuditLog.log_unauthorized_access(
            endpoint=f"/api/queue/{action_id}/approve",
            ip_address=client_ip,
            reason="permission_denied",
            attempted_user_id=str(current_user.id),
        )
        raise AuthorizationError("You don't have permission to approve this action")

    # Check if already processed
    if action.status != ActionStatus.PENDING:
        logger.warning(f"Attempted to approve non-pending action {action_id}: {action.status.value}")
        raise ValidationError(f"Action is already {action.status.value}")

    # Update action
    try:
        action.status = ActionStatus.APPROVED
        action.approved_at = datetime.utcnow()
        action.resolved_at = datetime.utcnow()

        # Update objective status
        action.conversation.objective.status = ObjectiveStatus.HANDLED
        action.conversation.objective.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(action)

        # Log action approval
        await AuditLog.log_action(
            user_id=str(current_user.id),
            action_type="approve",
            resource_type="agent_action",
            resource_id=str(action_id),
            ip_address=client_ip,
            details={"notes": request.notes} if request.notes else None,
        )

        logger.info(f"User {current_user.id} approved action {action_id}")

        # TODO: Trigger actual Gmail send operation here
        # await gmail_service.send_email(action)
    except Exception as e:
        logger.error(f"Failed to approve action {action_id}: {e}", exc_info=True)
        raise DatabaseError("Failed to approve action")

    # Get latest message for response
    latest_message = None
    for msg in sorted(action.conversation.messages, key=lambda m: m.sent_at, reverse=True):
        if msg.direction == MessageDirection.INCOMING:
            latest_message = msg
            break

    if latest_message:
        queue_item = _action_to_queue_item(
            action,
            action.conversation,
            action.conversation.objective,
            latest_message
        )
    else:
        queue_item = None

    return ActionResponse(
        success=True,
        message="Action approved and queued for execution",
        action_id=str(action.id),
        action=queue_item,
    )


@router.post("/{action_id}/override", response_model=ActionResponse)
async def override_action(
    req: Request,
    action_id: UUID,
    request: OverrideRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Override/reject the AI's proposed action.

    This will:
    1. Verify the action belongs to the current user
    2. Update status to 'rejected'
    3. Store the override reason for learning
    4. Mark the objective as waiting for user action
    """
    client_ip = get_client_ip(req)

    # Fetch the action with its relationships
    query = (
        select(AgentAction)
        .options(
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.objective),
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.messages),
        )
        .where(AgentAction.id == action_id)
    )

    result = await db.execute(query)
    action = result.unique().scalar_one_or_none()

    if not action:
        logger.warning(f"Override action: Action not found {action_id}")
        raise NotFoundError("Action", str(action_id))

    # Verify ownership
    if action.conversation.objective.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to override action {action_id} without permission")
        await AuditLog.log_unauthorized_access(
            endpoint=f"/api/queue/{action_id}/override",
            ip_address=client_ip,
            reason="permission_denied",
            attempted_user_id=str(current_user.id),
        )
        raise AuthorizationError("You don't have permission to override this action")

    # Check if already processed
    if action.status != ActionStatus.PENDING:
        logger.warning(f"Attempted to override non-pending action {action_id}: {action.status.value}")
        raise ValidationError(f"Action is already {action.status.value}")

    # Update action
    try:
        action.status = ActionStatus.REJECTED
        action.override_reason = request.reason
        action.resolved_at = datetime.utcnow()

        # Update objective status back to waiting on user
        action.conversation.objective.status = ObjectiveStatus.WAITING_ON_YOU
        action.conversation.objective.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(action)

        # Log action override/rejection
        await AuditLog.log_action(
            user_id=str(current_user.id),
            action_type="override",
            resource_type="agent_action",
            resource_id=str(action_id),
            ip_address=client_ip,
            details={"reason": request.reason},
        )

        logger.info(f"User {current_user.id} overrode action {action_id}: {request.reason}")

        # TODO: Log for policy training and improvement
        # await policy_service.learn_from_override(action, request.reason)
    except Exception as e:
        logger.error(f"Failed to override action {action_id}: {e}", exc_info=True)
        raise DatabaseError("Failed to override action")

    return ActionResponse(
        success=True,
        message="Action overridden successfully",
        action_id=str(action.id),
    )


@router.post("/{action_id}/edit", response_model=ActionResponse)
async def edit_action(
    req: Request,
    action_id: UUID,
    request: EditRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Edit the AI's proposed action before sending.

    This will:
    1. Verify the action belongs to the current user
    2. Store the edited content in user_edit field
    3. Keep original in proposed_content
    4. Update status to 'edited'
    5. Mark it ready for execution with edited content
    """
    client_ip = get_client_ip(req)

    # Fetch the action with its relationships
    query = (
        select(AgentAction)
        .options(
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.objective),
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.messages),
        )
        .where(AgentAction.id == action_id)
    )

    result = await db.execute(query)
    action = result.unique().scalar_one_or_none()

    if not action:
        logger.warning(f"Edit action: Action not found {action_id}")
        raise NotFoundError("Action", str(action_id))

    # Verify ownership
    if action.conversation.objective.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to edit action {action_id} without permission")
        await AuditLog.log_unauthorized_access(
            endpoint=f"/api/queue/{action_id}/edit",
            ip_address=client_ip,
            reason="permission_denied",
            attempted_user_id=str(current_user.id),
        )
        raise AuthorizationError("You don't have permission to edit this action")

    # Check if already processed
    if action.status != ActionStatus.PENDING:
        logger.warning(f"Attempted to edit non-pending action {action_id}: {action.status.value}")
        raise ValidationError(f"Action is already {action.status.value}")

    # Update action
    try:
        action.status = ActionStatus.EDITED
        action.user_edit = request.edited_content
        action.approved_at = datetime.utcnow()
        action.resolved_at = datetime.utcnow()

        # Update objective status
        action.conversation.objective.status = ObjectiveStatus.HANDLED
        action.conversation.objective.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(action)

        # Log action edit
        await AuditLog.log_action(
            user_id=str(current_user.id),
            action_type="edit",
            resource_type="agent_action",
            resource_id=str(action_id),
            ip_address=client_ip,
            details={"original_length": len(action.proposed_content), "edited_length": len(request.edited_content)},
        )

        logger.info(f"User {current_user.id} edited action {action_id}")

        # TODO: Trigger actual Gmail send with edited content
        # await gmail_service.send_email(action, use_edited=True)

        # TODO: Log for policy training to understand user preferences
        # await policy_service.learn_from_edit(action, request.edited_content)
    except Exception as e:
        logger.error(f"Failed to edit action {action_id}: {e}", exc_info=True)
        raise DatabaseError("Failed to edit action")

    # Get latest message for response
    latest_message = None
    for msg in sorted(action.conversation.messages, key=lambda m: m.sent_at, reverse=True):
        if msg.direction == MessageDirection.INCOMING:
            latest_message = msg
            break

    if latest_message:
        queue_item = _action_to_queue_item(
            action,
            action.conversation,
            action.conversation.objective,
            latest_message
        )
    else:
        queue_item = None

    return ActionResponse(
        success=True,
        message="Action edited and queued for execution",
        action_id=str(action.id),
        action=queue_item,
    )


@router.post("/{action_id}/escalate", response_model=ActionResponse)
async def escalate_action(
    req: Request,
    action_id: UUID,
    request: EscalateRequest = EscalateRequest(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Escalate an action for more context or team review.

    This will:
    1. Verify the action belongs to the current user
    2. Update risk_level to 'high'
    3. Add escalation note
    4. Keep status as pending
    5. Optionally notify team members (placeholder)
    """
    client_ip = get_client_ip(req)

    # Fetch the action with its relationships
    query = (
        select(AgentAction)
        .options(
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.objective),
            joinedload(AgentAction.conversation)
            .joinedload(Conversation.messages),
        )
        .where(AgentAction.id == action_id)
    )

    result = await db.execute(query)
    action = result.unique().scalar_one_or_none()

    if not action:
        logger.warning(f"Escalate action: Action not found {action_id}")
        raise NotFoundError("Action", str(action_id))

    # Verify ownership
    if action.conversation.objective.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to escalate action {action_id} without permission")
        await AuditLog.log_unauthorized_access(
            endpoint=f"/api/queue/{action_id}/escalate",
            ip_address=client_ip,
            reason="permission_denied",
            attempted_user_id=str(current_user.id),
        )
        raise AuthorizationError("You don't have permission to escalate this action")

    # Update action
    try:
        action.risk_level = RiskLevel.HIGH
        action.escalation_note = request.reason or "Escalated for team review"

        # Update objective
        action.conversation.objective.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(action)

        # Log action escalation
        await AuditLog.log_action(
            user_id=str(current_user.id),
            action_type="escalate",
            resource_type="agent_action",
            resource_id=str(action_id),
            ip_address=client_ip,
            details={"reason": request.reason, "notify_team": request.notify_team},
        )

        logger.info(f"User {current_user.id} escalated action {action_id}")

        # TODO: Implement team notification if requested
        # if request.notify_team:
        #     await notification_service.notify_team(action, request.reason)
    except Exception as e:
        logger.error(f"Failed to escalate action {action_id}: {e}", exc_info=True)
        raise DatabaseError("Failed to escalate action")

    return ActionResponse(
        success=True,
        message="Action escalated for review",
        action_id=str(action.id),
    )


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get efficiency statistics for the current user.

    Calculates:
    - Total emails received
    - Emails handled autonomously by AI
    - Emails pending review
    - Overall efficiency rate
    - Average confidence score
    - Average response time
    """
    # Time window: last 30 days
    time_window = datetime.utcnow() - timedelta(days=30)

    # Total emails (total messages received)
    total_query = (
        select(func.count(Message.id))
        .join(Message.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                Message.direction == MessageDirection.INCOMING,
                Message.created_at >= time_window
            )
        )
    )
    result = await db.execute(total_query)
    total_emails = result.scalar() or 0

    # Emails handled by AI (approved + edited actions)
    handled_query = (
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
                AgentAction.created_at >= time_window
            )
        )
    )
    result = await db.execute(handled_query)
    handled_by_ai = result.scalar() or 0

    # Pending review
    pending_query = (
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
    result = await db.execute(pending_query)
    pending_review = result.scalar() or 0

    # Calculate efficiency rate
    efficiency_rate = 0.0
    if total_emails > 0:
        efficiency_rate = (handled_by_ai / total_emails) * 100

    # Average confidence score
    avg_confidence_query = (
        select(func.avg(AgentAction.confidence_score))
        .join(AgentAction.conversation)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                AgentAction.created_at >= time_window
            )
        )
    )
    result = await db.execute(avg_confidence_query)
    avg_confidence = result.scalar() or 0.0
    avg_confidence = float(avg_confidence) * 100  # Convert to percentage

    # Average response time (time between message received and action approved)
    # This is more complex - we need to join messages with actions
    avg_response_query = (
        select(
            func.avg(
                func.extract('epoch', AgentAction.approved_at - Message.sent_at)
            )
        )
        .join(AgentAction.conversation)
        .join(Conversation.messages)
        .join(Conversation.objective)
        .where(
            and_(
                Objective.user_id == current_user.id,
                AgentAction.approved_at.isnot(None),
                Message.direction == MessageDirection.INCOMING,
                AgentAction.created_at >= time_window
            )
        )
    )
    result = await db.execute(avg_response_query)
    avg_response_time = result.scalar()
    if avg_response_time:
        avg_response_time = float(avg_response_time) / 3600  # Convert to hours

    return StatsResponse(
        total_emails=total_emails,
        handled_by_ai=handled_by_ai,
        pending_review=pending_review,
        efficiency_rate=round(efficiency_rate, 1),
        avg_confidence=round(avg_confidence, 1),
        avg_response_time=round(avg_response_time, 2) if avg_response_time else None,
    )
