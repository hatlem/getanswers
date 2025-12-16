"""Unit tests for the AgentService.

This test suite validates the Claude AI Agent service functionality.
Run with: pytest app/services/test_agent.py
"""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch

from .agent import (
    AgentService,
    EmailAnalysis,
    DraftResponse,
    RiskAssessment,
    PolicyMatch,
    EmailIntent,
    ExtractedEntity,
)
from ..models.message import Message, MessageDirection
from ..models.policy import Policy
from ..models.user import AutonomyLevel
from ..models.agent_action import ActionType, RiskLevel


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    with patch('app.services.agent.anthropic.Anthropic') as mock:
        yield mock


@pytest.fixture
def agent_service(mock_anthropic_client):
    """Create an AgentService instance with mocked client."""
    return AgentService(api_key="test-api-key")


@pytest.fixture
def sample_message():
    """Create a sample email message."""
    return Message(
        id=uuid4(),
        conversation_id=uuid4(),
        gmail_message_id="msg_test_001",
        sender_email="sender@example.com",
        sender_name="John Doe",
        subject="Test Subject",
        body_text="This is a test email body.",
        body_html="<html>This is a test email body.</html>",
        direction=MessageDirection.INCOMING,
        sent_at=datetime.utcnow(),
        created_at=datetime.utcnow()
    )


@pytest.fixture
def sample_conversation_context():
    """Create sample conversation context."""
    return [
        Message(
            id=uuid4(),
            conversation_id=uuid4(),
            gmail_message_id="msg_prev_001",
            sender_email="user@company.com",
            sender_name="Current User",
            subject="Re: Previous topic",
            body_text="Previous message in thread.",
            body_html="<html>Previous message in thread.</html>",
            direction=MessageDirection.OUTGOING,
            sent_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
    ]


@pytest.fixture
def sample_policy():
    """Create a sample user policy."""
    return Policy(
        id=uuid4(),
        user_id=uuid4(),
        name="Test Policy",
        description="A test automation policy",
        rules={
            "conditions": [
                {"field": "subject", "contains": "test"}
            ],
            "actions": [
                {"type": "draft", "template": "standard"}
            ]
        },
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def sample_analysis():
    """Create a sample email analysis."""
    return EmailAnalysis(
        intent=EmailIntent(
            primary="question",
            secondary=None,
            description="The sender is asking about project status"
        ),
        sentiment="neutral",
        tone="professional",
        urgency="medium",
        requires_immediate_response=False,
        category="question",
        is_actionable=True,
        extracted_entities=[
            ExtractedEntity(type="project", value="Project X", confidence=0.9)
        ],
        key_points=["Asking about project status", "Needs update by Friday"],
        sender_relationship="colleague",
        is_likely_spam=False,
        context_summary="Ongoing discussion about Project X"
    )


@pytest.fixture
def sample_draft():
    """Create a sample draft response."""
    return DraftResponse(
        subject="Re: Test Subject",
        body="Hi John,\n\nThanks for reaching out. Here's the update on Project X...\n\nBest regards",
        suggested_action=ActionType.DRAFT,
        reasoning="This is a straightforward question that requires a factual response",
        alternative_tone=None,
        key_considerations=["Provide specific timeline", "Mention blockers if any"]
    )


# =============================================================================
# Helper Method Tests
# =============================================================================

def test_format_conversation_context_empty(agent_service):
    """Test formatting empty conversation context."""
    result = agent_service._format_conversation_context([])
    assert result == ""


def test_format_conversation_context_with_messages(agent_service, sample_conversation_context):
    """Test formatting conversation context with messages."""
    result = agent_service._format_conversation_context(sample_conversation_context)
    assert "SENT" in result or "RECEIVED" in result
    assert "Previous message" in result


def test_assess_intent_clarity_high(agent_service):
    """Test intent clarity assessment for clear email."""
    analysis = EmailAnalysis(
        intent=EmailIntent(
            primary="request",
            description="Please send the quarterly report"
        ),
        sentiment="neutral",
        tone="professional",
        urgency="medium",
        requires_immediate_response=False,
        category="request",
        is_actionable=True,
        extracted_entities=[],
        key_points=["Send quarterly report"],
        sender_relationship="colleague",
        is_likely_spam=False,
        context_summary="Work-related request"
    )

    clarity = agent_service._assess_intent_clarity(analysis)
    assert 0 <= clarity <= 1
    assert clarity > 0.5  # Should be relatively high


def test_assess_intent_clarity_spam(agent_service):
    """Test intent clarity for spam email."""
    analysis = EmailAnalysis(
        intent=EmailIntent(primary="spam", description="Unknown intent"),
        sentiment="neutral",
        tone="generic",
        urgency="low",
        requires_immediate_response=False,
        category="unknown",
        is_actionable=False,
        extracted_entities=[],
        key_points=[],
        sender_relationship="unknown",
        is_likely_spam=True,
        context_summary="Suspicious email"
    )

    clarity = agent_service._assess_intent_clarity(analysis)
    assert clarity < 0.5  # Should be low for spam


def test_assess_response_quality(agent_service, sample_message, sample_analysis, sample_draft):
    """Test response quality assessment."""
    quality = agent_service._assess_response_quality(
        sample_message, sample_analysis, sample_draft
    )
    assert 0 <= quality <= 1


def test_assess_context_familiarity_no_context(agent_service, sample_message, sample_analysis):
    """Test context familiarity with no conversation history."""
    familiarity = agent_service._assess_context_familiarity(
        sample_message, [], sample_analysis
    )
    assert 0 <= familiarity <= 1
    # Base 0.3 + sender_relationship "colleague" 0.2 + clear category 0.1 = 0.6
    assert familiarity <= 0.7  # Should be moderate without conversation context


def test_assess_context_familiarity_with_context(
    agent_service, sample_message, sample_conversation_context, sample_analysis
):
    """Test context familiarity with conversation history."""
    familiarity = agent_service._assess_context_familiarity(
        sample_message, sample_conversation_context, sample_analysis
    )
    assert 0 <= familiarity <= 1
    assert familiarity > 0.3  # Should be higher with context


def test_calculate_risk_adjustment_safe(agent_service):
    """Test risk adjustment for safe emails."""
    analysis = EmailAnalysis(
        intent=EmailIntent(primary="fyi", description="Just an update"),
        sentiment="positive",
        tone="friendly",
        urgency="low",
        requires_immediate_response=False,
        category="update",
        is_actionable=False,
        extracted_entities=[],
        key_points=["Status update"],
        sender_relationship="colleague",
        is_likely_spam=False,
        context_summary="Regular update"
    )

    adjustment = agent_service._calculate_risk_adjustment(analysis)
    assert -0.5 <= adjustment <= 1.0
    assert adjustment > 0  # Should be positive for safe emails


def test_calculate_risk_adjustment_spam(agent_service):
    """Test risk adjustment for spam."""
    analysis = EmailAnalysis(
        intent=EmailIntent(primary="spam", description="Suspicious"),
        sentiment="neutral",
        tone="generic",
        urgency="high",
        requires_immediate_response=True,
        category="unknown",
        is_actionable=False,
        extracted_entities=[],
        key_points=[],
        sender_relationship="unknown",
        is_likely_spam=True,
        context_summary="Spam email"
    )

    adjustment = agent_service._calculate_risk_adjustment(analysis)
    assert adjustment < 0  # Should be negative for spam


# =============================================================================
# Auto-Execution Logic Tests
# =============================================================================

@pytest.mark.asyncio
async def test_should_auto_execute_high_autonomy_low_risk():
    """Test auto-execution with high autonomy and low risk."""
    agent = AgentService(api_key="test-key")

    result = await agent.should_auto_execute(
        confidence=75.0,
        risk_level=RiskLevel.LOW,
        autonomy_level=AutonomyLevel.HIGH,
        action_type=ActionType.DRAFT
    )

    assert result is True


@pytest.mark.asyncio
async def test_should_auto_execute_high_autonomy_low_confidence():
    """Test auto-execution with high autonomy but low confidence."""
    agent = AgentService(api_key="test-key")

    result = await agent.should_auto_execute(
        confidence=60.0,
        risk_level=RiskLevel.LOW,
        autonomy_level=AutonomyLevel.HIGH,
        action_type=ActionType.DRAFT
    )

    assert result is False


@pytest.mark.asyncio
async def test_should_auto_execute_medium_autonomy():
    """Test auto-execution with medium autonomy."""
    agent = AgentService(api_key="test-key")

    # Should auto-execute with high confidence
    result_high = await agent.should_auto_execute(
        confidence=90.0,
        risk_level=RiskLevel.LOW,
        autonomy_level=AutonomyLevel.MEDIUM,
        action_type=ActionType.DRAFT
    )
    assert result_high is True

    # Should not auto-execute with medium confidence
    result_medium = await agent.should_auto_execute(
        confidence=75.0,
        risk_level=RiskLevel.LOW,
        autonomy_level=AutonomyLevel.MEDIUM,
        action_type=ActionType.DRAFT
    )
    assert result_medium is False


@pytest.mark.asyncio
async def test_should_auto_execute_low_autonomy():
    """Test auto-execution with low autonomy."""
    agent = AgentService(api_key="test-key")

    result = await agent.should_auto_execute(
        confidence=95.0,
        risk_level=RiskLevel.LOW,
        autonomy_level=AutonomyLevel.LOW,
        action_type=ActionType.DRAFT
    )

    assert result is False


@pytest.mark.asyncio
async def test_should_auto_execute_high_risk():
    """Test auto-execution with high risk."""
    agent = AgentService(api_key="test-key")

    result = await agent.should_auto_execute(
        confidence=95.0,
        risk_level=RiskLevel.HIGH,
        autonomy_level=AutonomyLevel.HIGH,
        action_type=ActionType.DRAFT
    )

    assert result is False


@pytest.mark.asyncio
async def test_should_auto_execute_medium_risk():
    """Test auto-execution with medium risk."""
    agent = AgentService(api_key="test-key")

    result = await agent.should_auto_execute(
        confidence=95.0,
        risk_level=RiskLevel.MEDIUM,
        autonomy_level=AutonomyLevel.HIGH,
        action_type=ActionType.DRAFT
    )

    assert result is False


@pytest.mark.asyncio
async def test_should_auto_execute_send_action():
    """Test auto-execution for SEND action requires higher confidence."""
    agent = AgentService(api_key="test-key")

    # SEND actions require +10% confidence
    result_low = await agent.should_auto_execute(
        confidence=75.0,  # Would work for DRAFT but not SEND
        risk_level=RiskLevel.LOW,
        autonomy_level=AutonomyLevel.HIGH,
        action_type=ActionType.SEND
    )
    assert result_low is False

    result_high = await agent.should_auto_execute(
        confidence=85.0,  # Higher confidence for SEND
        risk_level=RiskLevel.LOW,
        autonomy_level=AutonomyLevel.HIGH,
        action_type=ActionType.SEND
    )
    assert result_high is True


# =============================================================================
# Confidence Calculation Tests
# =============================================================================

@pytest.mark.asyncio
async def test_calculate_confidence_bounds(
    agent_service, sample_message, sample_analysis, sample_draft
):
    """Test that confidence scores are within valid bounds."""
    confidence = await agent_service.calculate_confidence(
        message=sample_message,
        analysis=sample_analysis,
        draft=sample_draft,
        conversation_context=[],
        user_historical_acceptance_rate=0.85
    )

    assert 0 <= confidence <= 100


@pytest.mark.asyncio
async def test_calculate_confidence_with_history(
    agent_service, sample_message, sample_analysis, sample_draft
):
    """Test confidence calculation with historical acceptance rate."""
    # High historical acceptance should increase confidence
    confidence_high_history = await agent_service.calculate_confidence(
        message=sample_message,
        analysis=sample_analysis,
        draft=sample_draft,
        conversation_context=[],
        user_historical_acceptance_rate=0.95
    )

    # Low historical acceptance should decrease confidence
    confidence_low_history = await agent_service.calculate_confidence(
        message=sample_message,
        analysis=sample_analysis,
        draft=sample_draft,
        conversation_context=[],
        user_historical_acceptance_rate=0.50
    )

    assert confidence_high_history > confidence_low_history


@pytest.mark.asyncio
async def test_calculate_confidence_no_history(
    agent_service, sample_message, sample_analysis, sample_draft
):
    """Test confidence calculation without historical data."""
    confidence = await agent_service.calculate_confidence(
        message=sample_message,
        analysis=sample_analysis,
        draft=sample_draft,
        conversation_context=[],
        user_historical_acceptance_rate=None
    )

    assert 0 <= confidence <= 100


# =============================================================================
# Prompt Building Tests
# =============================================================================

def test_build_analysis_system_prompt(agent_service):
    """Test analysis system prompt generation."""
    prompt = agent_service._build_analysis_system_prompt(
        user_email="test@company.com",
        user_name="Test User"
    )

    assert "Test User" in prompt
    assert "test@company.com" in prompt
    assert "executive assistant" in prompt.lower()


def test_build_response_system_prompt(agent_service):
    """Test response generation system prompt."""
    prompt = agent_service._build_response_system_prompt(
        user_email="test@company.com",
        user_name="Test User",
        user_preferences={"communication_tone": "formal"}
    )

    assert "Test User" in prompt
    assert "test@company.com" in prompt
    assert "formal" in prompt


def test_build_risk_assessment_prompt(agent_service):
    """Test risk assessment prompt generation."""
    prompt = agent_service._build_risk_assessment_prompt()

    assert "risk" in prompt.lower()
    assert "financial" in prompt.lower()
    assert "legal" in prompt.lower()


def test_build_policy_evaluation_prompt(agent_service):
    """Test policy evaluation prompt generation."""
    prompt = agent_service._build_policy_evaluation_prompt()

    assert "policy" in prompt.lower()
    assert "rules" in prompt.lower()


# =============================================================================
# Integration Tests (require API key)
# =============================================================================

@pytest.mark.integration
@pytest.mark.asyncio
async def test_analyze_email_integration(sample_message):
    """Integration test for email analysis (requires API key)."""
    # Skip if no API key
    pytest.importorskip("anthropic")

    import os
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("ANTHROPIC_API_KEY not set")

    agent = AgentService(api_key=api_key)

    analysis = await agent.analyze_email(
        message=sample_message,
        conversation_context=[],
        user_email="test@company.com",
        user_name="Test User"
    )

    assert isinstance(analysis, EmailAnalysis)
    assert analysis.intent is not None
    assert analysis.sentiment is not None
    assert analysis.category is not None


if __name__ == "__main__":
    # Run tests with: python -m pytest app/services/test_agent.py -v
    pytest.main([__file__, "-v"])
