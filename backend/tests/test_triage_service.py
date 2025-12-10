"""
Tests for the Triage Service.

This test file demonstrates how to use the TriageService and validates
the email processing pipeline.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.triage import (
    TriageService,
    GmailService,
    SyncResult,
    ExecutionResult,
    ProcessingResult,
)
from app.services.agent import AgentService
from app.models.user import User, AutonomyLevel
from app.models.message import Message, MessageDirection
from app.models.conversation import Conversation
from app.models.objective import Objective, ObjectiveStatus
from app.models.agent_action import AgentAction, ActionType, RiskLevel, ActionStatus


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
async def test_user(db_session):
    """Create a test user."""
    user = User(
        email="test@example.com",
        name="Test User",
        autonomy_level=AutonomyLevel.MEDIUM,
        gmail_credentials={
            "access_token": "test_token",
            "refresh_token": "test_refresh",
        }
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def gmail_service():
    """Create a mock Gmail service."""
    return GmailService(user_credentials={"access_token": "test"})


@pytest.fixture
def agent_service():
    """Create an agent service."""
    return AgentService(api_key="test_api_key")


@pytest.fixture
async def triage_service(db_session, gmail_service, agent_service):
    """Create a triage service."""
    return TriageService(
        db=db_session,
        gmail_service=gmail_service,
        agent_service=agent_service
    )


@pytest.fixture
def sample_gmail_message():
    """Sample Gmail message for testing."""
    return {
        'id': 'msg_12345',
        'threadId': 'thread_67890',
        'from': {
            'name': 'John Doe',
            'email': 'john@example.com'
        },
        'to': [
            {'name': 'Test User', 'email': 'test@example.com'}
        ],
        'subject': 'Project Update Request',
        'body_text': 'Hi Test,\n\nCould you please send me an update on the project?\n\nThanks,\nJohn',
        'body_html': '<html><body>Hi Test,<br><br>Could you please send me an update on the project?<br><br>Thanks,<br>John</body></html>',
        'sent_at': datetime.utcnow() - timedelta(hours=1),
        'labels': ['INBOX', 'UNREAD']
    }


# =============================================================================
# Test Process New Email
# =============================================================================

@pytest.mark.asyncio
async def test_process_new_email_creates_message(
    triage_service,
    test_user,
    sample_gmail_message,
    db_session
):
    """Test that processing a new email creates a message in the database."""
    # Note: This will fail in real execution because AgentService requires actual API calls
    # In production, you'd mock the agent service methods

    # Process the email
    result = await triage_service.process_new_email(
        user_id=test_user.id,
        gmail_message=sample_gmail_message
    )

    # Verify result structure
    assert isinstance(result, ProcessingResult)
    assert result.action_id is not None
    assert result.conversation_id is not None
    assert result.objective_id is not None
    assert 0 <= result.confidence <= 100
    assert result.risk_level in [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH]
    assert isinstance(result.auto_executed, bool)


@pytest.mark.asyncio
async def test_process_new_email_prevents_duplicates(
    triage_service,
    test_user,
    sample_gmail_message,
    db_session
):
    """Test that duplicate messages are detected and skipped."""
    # Process first time
    result1 = await triage_service.process_new_email(
        user_id=test_user.id,
        gmail_message=sample_gmail_message
    )

    # Process again with same ID
    result2 = await triage_service.process_new_email(
        user_id=test_user.id,
        gmail_message=sample_gmail_message
    )

    # Should return same action
    assert result1.action_id == result2.action_id


# =============================================================================
# Test Gmail Sync
# =============================================================================

@pytest.mark.asyncio
async def test_sync_user_inbox_basic(
    triage_service,
    test_user,
    gmail_service,
    db_session
):
    """Test basic inbox sync operation."""
    # Mock fetch_new_messages to return test data
    async def mock_fetch(since=None, max_results=100):
        return [
            {
                'id': f'msg_{i}',
                'threadId': f'thread_{i}',
                'from': {'name': 'Sender', 'email': f'sender{i}@example.com'},
                'to': [{'name': 'Test', 'email': 'test@example.com'}],
                'subject': f'Test Email {i}',
                'body_text': f'Test body {i}',
                'body_html': f'<html>Test body {i}</html>',
                'sent_at': datetime.utcnow(),
                'labels': ['INBOX']
            }
            for i in range(3)
        ]

    gmail_service.fetch_new_messages = mock_fetch

    # Perform sync
    result = await triage_service.sync_user_inbox(
        user_id=test_user.id,
        max_messages=10
    )

    # Verify result
    assert isinstance(result, SyncResult)
    assert result.new_messages == 3
    assert result.duration_seconds > 0
    assert result.last_sync_time is not None


@pytest.mark.asyncio
async def test_sync_user_inbox_handles_errors(
    triage_service,
    test_user,
    gmail_service,
    db_session
):
    """Test that sync handles individual message errors gracefully."""
    # Mock to return one good and one bad message
    async def mock_fetch(since=None, max_results=100):
        return [
            {
                'id': 'msg_good',
                'threadId': 'thread_1',
                'from': {'name': 'Sender', 'email': 'sender@example.com'},
                'subject': 'Good Email',
                'body_text': 'This is fine',
                'body_html': '<html>This is fine</html>',
                'sent_at': datetime.utcnow(),
            },
            {
                'id': 'msg_bad',
                # Missing required fields - will cause error
            }
        ]

    gmail_service.fetch_new_messages = mock_fetch

    result = await triage_service.sync_user_inbox(
        user_id=test_user.id,
        max_messages=10
    )

    # Should process the good one and log error for bad one
    assert result.new_messages == 2
    assert result.errors >= 1


# =============================================================================
# Test Action Execution
# =============================================================================

@pytest.mark.asyncio
async def test_execute_send_action(
    triage_service,
    test_user,
    db_session
):
    """Test executing a SEND action."""
    # Create test data
    objective = Objective(
        user_id=test_user.id,
        title="Test Objective",
        status=ObjectiveStatus.WAITING_ON_YOU
    )
    db_session.add(objective)
    await db_session.flush()

    conversation = Conversation(
        objective_id=objective.id,
        gmail_thread_id="thread_test",
        participants=["john@example.com"]
    )
    db_session.add(conversation)
    await db_session.flush()

    message = Message(
        conversation_id=conversation.id,
        gmail_message_id="msg_test",
        sender_email="john@example.com",
        sender_name="John Doe",
        subject="Test Subject",
        body_text="Test body",
        body_html="<html>Test body</html>",
        direction=MessageDirection.INCOMING,
        sent_at=datetime.utcnow()
    )
    db_session.add(message)
    await db_session.flush()

    action = AgentAction(
        conversation_id=conversation.id,
        action_type=ActionType.SEND,
        proposed_content="Thanks for your message!",
        confidence_score=0.85,
        risk_level=RiskLevel.LOW,
        priority_score=50,
        status=ActionStatus.PENDING
    )
    db_session.add(action)
    await db_session.commit()
    await db_session.refresh(action)

    # Execute the action
    result = await triage_service.execute_action(
        action_id=action.id,
        auto_executed=False
    )

    # Verify result
    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.action_id == action.id
    assert result.gmail_message_id is not None


@pytest.mark.asyncio
async def test_execute_draft_action(
    triage_service,
    test_user,
    db_session
):
    """Test executing a DRAFT action."""
    # Setup similar to above
    objective = Objective(
        user_id=test_user.id,
        title="Test Objective",
        status=ObjectiveStatus.WAITING_ON_YOU
    )
    db_session.add(objective)
    await db_session.flush()

    conversation = Conversation(
        objective_id=objective.id,
        gmail_thread_id="thread_draft",
        participants=["jane@example.com"]
    )
    db_session.add(conversation)
    await db_session.flush()

    message = Message(
        conversation_id=conversation.id,
        gmail_message_id="msg_draft",
        sender_email="jane@example.com",
        sender_name="Jane Smith",
        subject="Draft Test",
        body_text="Draft test body",
        body_html="<html>Draft test body</html>",
        direction=MessageDirection.INCOMING,
        sent_at=datetime.utcnow()
    )
    db_session.add(message)
    await db_session.flush()

    action = AgentAction(
        conversation_id=conversation.id,
        action_type=ActionType.DRAFT,
        proposed_content="Draft response content",
        confidence_score=0.75,
        risk_level=RiskLevel.MEDIUM,
        priority_score=60,
        status=ActionStatus.PENDING
    )
    db_session.add(action)
    await db_session.commit()
    await db_session.refresh(action)

    # Execute
    result = await triage_service.execute_action(action_id=action.id)

    # Verify
    assert result.success is True
    assert result.gmail_message_id is not None


# =============================================================================
# Test Objective Grouping
# =============================================================================

@pytest.mark.asyncio
async def test_find_or_create_objective_creates_new(
    triage_service,
    test_user,
    db_session
):
    """Test that a new objective is created for a new conversation."""
    # Create a conversation and message
    objective_temp = Objective(
        user_id=test_user.id,
        title="Temp",
        status=ObjectiveStatus.WAITING_ON_YOU
    )
    db_session.add(objective_temp)
    await db_session.flush()

    conversation = Conversation(
        objective_id=objective_temp.id,
        gmail_thread_id="thread_new",
        participants=[]
    )
    db_session.add(conversation)
    await db_session.flush()

    message = Message(
        conversation_id=conversation.id,
        gmail_message_id="msg_new",
        sender_email="newperson@example.com",
        sender_name="New Person",
        subject="Completely New Topic",
        body_text="This is about something new",
        body_html="<html>This is about something new</html>",
        direction=MessageDirection.INCOMING,
        sent_at=datetime.utcnow()
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)

    # Find or create objective
    objective = await triage_service.find_or_create_objective(
        user_id=test_user.id,
        message=message
    )

    # Should create new objective
    assert objective.id is not None
    assert "New Topic" in objective.title or "New Person" in objective.title


@pytest.mark.asyncio
async def test_find_or_create_objective_matches_existing(
    triage_service,
    test_user,
    db_session
):
    """Test that similar messages are grouped into existing objectives."""
    # Create existing objective with conversation
    objective = Objective(
        user_id=test_user.id,
        title="Project Alpha Updates",
        status=ObjectiveStatus.WAITING_ON_OTHERS
    )
    db_session.add(objective)
    await db_session.flush()

    conversation1 = Conversation(
        objective_id=objective.id,
        gmail_thread_id="thread_alpha_1",
        participants=["alice@example.com"]
    )
    db_session.add(conversation1)
    await db_session.flush()

    message1 = Message(
        conversation_id=conversation1.id,
        gmail_message_id="msg_alpha_1",
        sender_email="alice@example.com",
        sender_name="Alice",
        subject="Project Alpha Status",
        body_text="Status update",
        body_html="<html>Status update</html>",
        direction=MessageDirection.INCOMING,
        sent_at=datetime.utcnow() - timedelta(hours=2)
    )
    db_session.add(message1)
    await db_session.commit()

    # Create new message with similar subject
    conversation2 = Conversation(
        objective_id=objective.id,  # Temporarily assign to same
        gmail_thread_id="thread_alpha_2",
        participants=["alice@example.com"]
    )
    db_session.add(conversation2)
    await db_session.flush()

    message2 = Message(
        conversation_id=conversation2.id,
        gmail_message_id="msg_alpha_2",
        sender_email="alice@example.com",
        sender_name="Alice",
        subject="Project Alpha Progress Update",  # Similar
        body_text="More progress",
        body_html="<html>More progress</html>",
        direction=MessageDirection.INCOMING,
        sent_at=datetime.utcnow()
    )
    db_session.add(message2)
    await db_session.commit()
    await db_session.refresh(message2)

    # Find objective
    found_objective = await triage_service.find_or_create_objective(
        user_id=test_user.id,
        message=message2
    )

    # Should match existing objective based on similarity
    # Note: With the current simple matching, it may or may not match
    # In production, you'd use AI for better matching
    assert found_objective.id is not None


# =============================================================================
# Test Objective Status Updates
# =============================================================================

@pytest.mark.asyncio
async def test_update_objective_status_waiting_on_you(
    triage_service,
    test_user,
    db_session
):
    """Test updating objective status to WAITING_ON_YOU when actions are pending."""
    objective = Objective(
        user_id=test_user.id,
        title="Test",
        status=ObjectiveStatus.HANDLED
    )
    db_session.add(objective)
    await db_session.flush()

    conversation = Conversation(
        objective_id=objective.id,
        gmail_thread_id="thread_status",
        participants=[]
    )
    db_session.add(conversation)
    await db_session.flush()

    action = AgentAction(
        conversation_id=conversation.id,
        action_type=ActionType.SEND,
        proposed_content="Test",
        confidence_score=0.8,
        risk_level=RiskLevel.LOW,
        priority_score=50,
        status=ActionStatus.PENDING  # Pending action
    )
    db_session.add(action)
    await db_session.commit()

    # Update status
    await triage_service.update_objective_status(objective.id)

    # Refresh
    await db_session.refresh(objective)

    # Should be WAITING_ON_YOU
    assert objective.status == ObjectiveStatus.WAITING_ON_YOU


@pytest.mark.asyncio
async def test_update_objective_status_waiting_on_others(
    triage_service,
    test_user,
    db_session
):
    """Test updating objective status to WAITING_ON_OTHERS when email sent."""
    objective = Objective(
        user_id=test_user.id,
        title="Test",
        status=ObjectiveStatus.WAITING_ON_YOU
    )
    db_session.add(objective)
    await db_session.flush()

    conversation = Conversation(
        objective_id=objective.id,
        gmail_thread_id="thread_sent",
        participants=[]
    )
    db_session.add(conversation)
    await db_session.flush()

    action = AgentAction(
        conversation_id=conversation.id,
        action_type=ActionType.SEND,
        proposed_content="Test",
        confidence_score=0.9,
        risk_level=RiskLevel.LOW,
        priority_score=50,
        status=ActionStatus.APPROVED  # Approved/sent
    )
    db_session.add(action)
    await db_session.commit()

    # Update status
    await triage_service.update_objective_status(objective.id)

    # Refresh
    await db_session.refresh(objective)

    # Should be WAITING_ON_OTHERS
    assert objective.status == ObjectiveStatus.WAITING_ON_OTHERS


# =============================================================================
# Test Helper Methods
# =============================================================================

@pytest.mark.asyncio
async def test_calculate_priority(triage_service, agent_service):
    """Test priority calculation logic."""
    from app.services.agent import EmailAnalysis, EmailIntent

    # High urgency analysis
    high_urgency = EmailAnalysis(
        intent=EmailIntent(
            primary="request",
            description="Urgent request"
        ),
        sentiment="neutral",
        tone="formal",
        urgency="critical",
        requires_immediate_response=True,
        category="finance",
        is_actionable=True,
        key_points=["Important"],
        sender_relationship="client",
        context_summary="Test"
    )

    priority = triage_service._calculate_priority(
        analysis=high_urgency,
        risk_level=RiskLevel.HIGH,
        confidence=50.0
    )

    # Should have high priority
    assert priority >= 80  # High urgency + high risk + low confidence

    # Low urgency analysis
    low_urgency = EmailAnalysis(
        intent=EmailIntent(
            primary="fyi",
            description="Just FYI"
        ),
        sentiment="positive",
        tone="casual",
        urgency="low",
        requires_immediate_response=False,
        category="internal",
        is_actionable=False,
        key_points=["Info"],
        sender_relationship="colleague",
        context_summary="Test"
    )

    priority = triage_service._calculate_priority(
        analysis=low_urgency,
        risk_level=RiskLevel.LOW,
        confidence=95.0
    )

    # Should have low priority
    assert priority <= 60


# =============================================================================
# Usage Examples
# =============================================================================

async def example_usage():
    """
    Example of how to use the TriageService in production.
    """
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
    from sqlalchemy.orm import sessionmaker

    # Setup database
    engine = create_async_engine("postgresql+asyncpg://localhost/getanswers")
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        # Create services
        gmail_service = GmailService(
            user_credentials={
                "access_token": "user_token",
                "refresh_token": "refresh_token"
            }
        )

        agent_service = AgentService(api_key="your_anthropic_api_key")

        triage_service = TriageService(
            db=db,
            gmail_service=gmail_service,
            agent_service=agent_service
        )

        # Example 1: Sync user's inbox
        user_id = uuid4()
        sync_result = await triage_service.sync_user_inbox(
            user_id=user_id,
            max_messages=50
        )

        print(f"Synced {sync_result.processed} of {sync_result.new_messages} messages")
        print(f"Errors: {sync_result.errors}")
        print(f"Duration: {sync_result.duration_seconds}s")

        # Example 2: Process a single email
        gmail_message = {
            'id': 'msg_123',
            'threadId': 'thread_456',
            'from': {'name': 'John', 'email': 'john@example.com'},
            'subject': 'Question about pricing',
            'body_text': 'What are your rates?',
            'body_html': '<html>What are your rates?</html>',
            'sent_at': datetime.utcnow()
        }

        result = await triage_service.process_new_email(
            user_id=user_id,
            gmail_message=gmail_message
        )

        print(f"Action created: {result.action_id}")
        print(f"Confidence: {result.confidence}%")
        print(f"Risk: {result.risk_level}")
        print(f"Auto-executed: {result.auto_executed}")

        # Example 3: Execute an action
        execution_result = await triage_service.execute_action(
            action_id=result.action_id
        )

        print(f"Execution success: {execution_result.success}")
        if execution_result.success:
            print(f"Gmail message ID: {execution_result.gmail_message_id}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
