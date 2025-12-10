"""API Integration Examples for AgentService.

This file demonstrates how to integrate the AgentService into FastAPI route handlers.
These are example implementations that show the recommended patterns.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from .agent import AgentService
from .dependencies import get_agent_service
from ..models.user import User, AutonomyLevel
from ..models.message import Message
from ..models.conversation import Conversation
from ..models.policy import Policy
from ..models.agent_action import AgentAction, ActionStatus, ActionType, RiskLevel


# =============================================================================
# Request/Response Models
# =============================================================================

class AnalyzeEmailRequest(BaseModel):
    """Request to analyze an email."""
    conversation_id: UUID


class AnalyzeEmailResponse(BaseModel):
    """Response with email analysis."""
    analysis: dict
    confidence: float
    risk_level: RiskLevel
    should_auto_execute: bool

    class Config:
        from_attributes = True


class GenerateResponseRequest(BaseModel):
    """Request to generate an email response."""
    conversation_id: UUID
    user_preferences: Optional[dict] = None


class GenerateResponseResponse(BaseModel):
    """Response with generated draft."""
    draft: dict
    action_id: UUID
    auto_execute: bool

    class Config:
        from_attributes = True


class ProcessConversationResponse(BaseModel):
    """Complete processing response."""
    conversation_id: UUID
    analysis: dict
    draft: dict
    risk_assessment: dict
    policy_matches: list[dict]
    confidence: float
    auto_execute: bool
    action_id: UUID

    class Config:
        from_attributes = True


# =============================================================================
# Example Router
# =============================================================================

router = APIRouter(prefix="/ai", tags=["AI Agent"])


# =============================================================================
# Email Analysis Endpoint
# =============================================================================

@router.post("/analyze/{conversation_id}", response_model=AnalyzeEmailResponse)
async def analyze_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),  # type: ignore
    current_user: User = Depends(get_current_user),  # type: ignore
    agent: AgentService = Depends(get_agent_service)
):
    """Analyze the latest email in a conversation.

    This endpoint analyzes an incoming email and returns:
    - Detailed analysis (intent, sentiment, urgency, etc.)
    - Confidence score for automated response
    - Risk assessment
    - Whether the action should be auto-executed

    Args:
        conversation_id: ID of the conversation to analyze
        db: Database session
        current_user: Current authenticated user
        agent: AI agent service

    Returns:
        Analysis results and recommendations

    Raises:
        HTTPException: If conversation not found or not authorized
    """
    # Get conversation and verify ownership
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    # Verify user owns this conversation
    await verify_conversation_ownership(db, conversation, current_user.id)

    # Get all messages in conversation
    messages = await get_messages_by_conversation(db, conversation_id)
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No messages found in conversation"
        )

    # Get the latest incoming message
    latest_message = messages[-1]

    # Get conversation context (previous messages)
    context_messages = messages[:-1]

    # Get user's active policies
    policies = await get_active_user_policies(db, current_user.id)

    # Analyze the email
    analysis = await agent.analyze_email(
        message=latest_message,
        conversation_context=context_messages,
        user_email=current_user.email,
        user_name=current_user.name
    )

    # Generate draft response
    draft = await agent.generate_response(
        message=latest_message,
        conversation_context=context_messages,
        analysis=analysis,
        user_email=current_user.email,
        user_name=current_user.name
    )

    # Assess risk
    risk = await agent.assess_risk(
        message=latest_message,
        analysis=analysis,
        policies=policies,
        conversation_context=context_messages
    )

    # Calculate confidence
    user_stats = await get_user_agent_stats(db, current_user.id)
    confidence = await agent.calculate_confidence(
        message=latest_message,
        analysis=analysis,
        draft=draft,
        conversation_context=context_messages,
        user_historical_acceptance_rate=user_stats.get("acceptance_rate")
    )

    # Determine auto-execution
    should_auto_execute = await agent.should_auto_execute(
        confidence=confidence,
        risk_level=risk.risk_level,
        autonomy_level=current_user.autonomy_level,
        action_type=draft.suggested_action
    )

    return AnalyzeEmailResponse(
        analysis=analysis.model_dump(),
        confidence=confidence,
        risk_level=risk.risk_level,
        should_auto_execute=should_auto_execute
    )


# =============================================================================
# Generate Response Endpoint
# =============================================================================

@router.post("/generate/{conversation_id}", response_model=GenerateResponseResponse)
async def generate_email_response(
    conversation_id: UUID,
    request: GenerateResponseRequest,
    db: AsyncSession = Depends(get_db),  # type: ignore
    current_user: User = Depends(get_current_user),  # type: ignore
    agent: AgentService = Depends(get_agent_service)
):
    """Generate an AI-powered email response.

    This endpoint generates a draft email response and creates an agent action
    record for tracking. If the action meets criteria for auto-execution,
    it will be marked as approved.

    Args:
        conversation_id: ID of the conversation
        request: Request with optional user preferences
        db: Database session
        current_user: Current authenticated user
        agent: AI agent service

    Returns:
        Generated draft and action details

    Raises:
        HTTPException: If conversation not found or not authorized
    """
    # Get and verify conversation
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    await verify_conversation_ownership(db, conversation, current_user.id)

    # Get messages
    messages = await get_messages_by_conversation(db, conversation_id)
    latest_message = messages[-1]
    context_messages = messages[:-1]

    # Get policies
    policies = await get_active_user_policies(db, current_user.id)

    # Full processing pipeline
    analysis = await agent.analyze_email(
        message=latest_message,
        conversation_context=context_messages,
        user_email=current_user.email,
        user_name=current_user.name
    )

    draft = await agent.generate_response(
        message=latest_message,
        conversation_context=context_messages,
        analysis=analysis,
        user_email=current_user.email,
        user_name=current_user.name,
        user_preferences=request.user_preferences
    )

    risk = await agent.assess_risk(
        message=latest_message,
        analysis=analysis,
        policies=policies,
        conversation_context=context_messages
    )

    user_stats = await get_user_agent_stats(db, current_user.id)
    confidence = await agent.calculate_confidence(
        message=latest_message,
        analysis=analysis,
        draft=draft,
        conversation_context=context_messages,
        user_historical_acceptance_rate=user_stats.get("acceptance_rate")
    )

    should_auto_execute = await agent.should_auto_execute(
        confidence=confidence,
        risk_level=risk.risk_level,
        autonomy_level=current_user.autonomy_level,
        action_type=draft.suggested_action
    )

    # Create agent action record
    action = AgentAction(
        conversation_id=conversation_id,
        action_type=draft.suggested_action,
        proposed_content=draft.body,
        confidence_score=confidence,
        risk_level=risk.risk_level,
        status=ActionStatus.APPROVED if should_auto_execute else ActionStatus.PENDING
    )

    db.add(action)
    await db.commit()
    await db.refresh(action)

    # If auto-executing, trigger email send
    if should_auto_execute:
        await execute_agent_action(db, action, draft, current_user)

    return GenerateResponseResponse(
        draft=draft.model_dump(),
        action_id=action.id,
        auto_execute=should_auto_execute
    )


# =============================================================================
# Complete Processing Endpoint
# =============================================================================

@router.post("/process/{conversation_id}", response_model=ProcessConversationResponse)
async def process_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),  # type: ignore
    current_user: User = Depends(get_current_user),  # type: ignore
    agent: AgentService = Depends(get_agent_service)
):
    """Process a conversation with complete AI analysis and response generation.

    This is the main endpoint for processing incoming emails. It performs:
    1. Email analysis
    2. Response generation
    3. Risk assessment
    4. Policy evaluation
    5. Confidence calculation
    6. Auto-execution decision
    7. Action logging

    Args:
        conversation_id: ID of the conversation to process
        db: Database session
        current_user: Current authenticated user
        agent: AI agent service

    Returns:
        Complete processing results

    Raises:
        HTTPException: If conversation not found or not authorized
    """
    # Get and verify conversation
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    await verify_conversation_ownership(db, conversation, current_user.id)

    # Get messages and policies
    messages = await get_messages_by_conversation(db, conversation_id)
    latest_message = messages[-1]
    context_messages = messages[:-1]
    policies = await get_active_user_policies(db, current_user.id)

    # Step 1: Analyze email
    analysis = await agent.analyze_email(
        message=latest_message,
        conversation_context=context_messages,
        user_email=current_user.email,
        user_name=current_user.name
    )

    # Step 2: Generate response
    draft = await agent.generate_response(
        message=latest_message,
        conversation_context=context_messages,
        analysis=analysis,
        user_email=current_user.email,
        user_name=current_user.name
    )

    # Step 3: Assess risk
    risk = await agent.assess_risk(
        message=latest_message,
        analysis=analysis,
        policies=policies,
        conversation_context=context_messages
    )

    # Step 4: Evaluate policies
    policy_matches = await agent.evaluate_policies(
        message=latest_message,
        analysis=analysis,
        policies=policies
    )

    # Step 5: Calculate confidence
    user_stats = await get_user_agent_stats(db, current_user.id)
    confidence = await agent.calculate_confidence(
        message=latest_message,
        analysis=analysis,
        draft=draft,
        conversation_context=context_messages,
        user_historical_acceptance_rate=user_stats.get("acceptance_rate")
    )

    # Step 6: Determine auto-execution
    should_auto_execute = await agent.should_auto_execute(
        confidence=confidence,
        risk_level=risk.risk_level,
        autonomy_level=current_user.autonomy_level,
        action_type=draft.suggested_action
    )

    # Step 7: Create action record
    action = AgentAction(
        conversation_id=conversation_id,
        action_type=draft.suggested_action,
        proposed_content=draft.body,
        confidence_score=confidence,
        risk_level=risk.risk_level,
        status=ActionStatus.APPROVED if should_auto_execute else ActionStatus.PENDING,
        resolved_at=datetime.utcnow() if should_auto_execute else None
    )

    db.add(action)
    await db.commit()
    await db.refresh(action)

    # Step 8: Auto-execute if appropriate
    if should_auto_execute:
        await execute_agent_action(db, action, draft, current_user)

    return ProcessConversationResponse(
        conversation_id=conversation_id,
        analysis=analysis.model_dump(),
        draft=draft.model_dump(),
        risk_assessment=risk.model_dump(),
        policy_matches=[m.model_dump() for m in policy_matches],
        confidence=confidence,
        auto_execute=should_auto_execute,
        action_id=action.id
    )


# =============================================================================
# Policy Testing Endpoint
# =============================================================================

@router.post("/test-policies/{conversation_id}")
async def test_policies_against_email(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),  # type: ignore
    current_user: User = Depends(get_current_user),  # type: ignore
    agent: AgentService = Depends(get_agent_service)
):
    """Test which policies would match against an email.

    This is useful for debugging and validating policy rules.

    Args:
        conversation_id: ID of the conversation
        db: Database session
        current_user: Current authenticated user
        agent: AI agent service

    Returns:
        List of matched policies with confidence scores

    Raises:
        HTTPException: If conversation not found or not authorized
    """
    # Get conversation
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    await verify_conversation_ownership(db, conversation, current_user.id)

    # Get messages and policies
    messages = await get_messages_by_conversation(db, conversation_id)
    latest_message = messages[-1]
    context_messages = messages[:-1]
    policies = await get_active_user_policies(db, current_user.id)

    # Analyze email first
    analysis = await agent.analyze_email(
        message=latest_message,
        conversation_context=context_messages,
        user_email=current_user.email,
        user_name=current_user.name
    )

    # Evaluate policies
    policy_matches = await agent.evaluate_policies(
        message=latest_message,
        analysis=analysis,
        policies=policies
    )

    return {
        "email_analysis": analysis.model_dump(),
        "policy_matches": [m.model_dump() for m in policy_matches],
        "total_policies": len(policies),
        "matched_policies": len(policy_matches)
    }


# =============================================================================
# Helper Functions (to be implemented in your actual codebase)
# =============================================================================

async def get_db():
    """Dependency for database session."""
    # Implement your database session logic
    raise NotImplementedError


async def get_current_user():
    """Dependency for current authenticated user."""
    # Implement your authentication logic
    raise NotImplementedError


async def get_conversation_by_id(db: AsyncSession, conversation_id: UUID) -> Optional[Conversation]:
    """Get conversation by ID."""
    # Implement database query
    raise NotImplementedError


async def verify_conversation_ownership(db: AsyncSession, conversation: Conversation, user_id: UUID):
    """Verify user owns the conversation."""
    # Implement ownership verification
    raise NotImplementedError


async def get_messages_by_conversation(db: AsyncSession, conversation_id: UUID) -> list[Message]:
    """Get all messages in a conversation."""
    # Implement database query
    raise NotImplementedError


async def get_active_user_policies(db: AsyncSession, user_id: UUID) -> list[Policy]:
    """Get user's active policies."""
    # Implement database query
    raise NotImplementedError


async def get_user_agent_stats(db: AsyncSession, user_id: UUID) -> dict:
    """Get user's historical agent statistics."""
    # Implement statistics calculation
    # Should return: {"acceptance_rate": 0.85, "total_actions": 100, ...}
    raise NotImplementedError


async def execute_agent_action(
    db: AsyncSession,
    action: AgentAction,
    draft: any,
    user: User
):
    """Execute an approved agent action (send email, etc.)."""
    # Implement action execution logic
    raise NotImplementedError


# =============================================================================
# Usage in main.py
# =============================================================================

"""
To use this router in your FastAPI app:

from app.services.api_integration_example import router as ai_router

app = FastAPI()
app.include_router(ai_router)
"""
