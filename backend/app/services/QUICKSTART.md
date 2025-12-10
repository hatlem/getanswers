# Claude AI Agent Service - Quick Start Guide

Get up and running with the AgentService in 5 minutes.

## Prerequisites

1. **API Key**: Get your Anthropic API key from https://console.anthropic.com/
2. **Environment**: Python 3.11+ with async support
3. **Dependencies**: `anthropic`, `pydantic`, `sqlalchemy`

## Setup

### 1. Install Dependencies

Already installed via `requirements.txt`:
```bash
cd /Users/andreashatlem/getanswers/backend
pip install -r requirements.txt
```

### 2. Configure API Key

Add to your `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

Or set environment variable:
```bash
export ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

### 3. Import the Service

```python
from app.services import AgentService, EmailAnalysis, DraftResponse
from app.core.config import settings

# Initialize
agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)
```

## Basic Usage

### Example 1: Analyze an Email (Simplest)

```python
from app.services import AgentService
from app.models.message import Message, MessageDirection
from datetime import datetime
from uuid import uuid4

# Initialize service
agent = AgentService(api_key="your-api-key")

# Create a message (or fetch from database)
message = Message(
    id=uuid4(),
    conversation_id=uuid4(),
    gmail_message_id="msg_123",
    sender_email="client@example.com",
    sender_name="John Client",
    subject="Quick question about the project",
    body_text="Hi, could you send me the latest status update? Thanks!",
    body_html="<html>...</html>",
    direction=MessageDirection.INCOMING,
    sent_at=datetime.utcnow(),
    created_at=datetime.utcnow()
)

# Analyze
analysis = await agent.analyze_email(
    message=message,
    conversation_context=[],  # Empty if first message
    user_email="you@company.com",
    user_name="Your Name"
)

# Use results
print(f"Intent: {analysis.intent.primary}")
print(f"Urgency: {analysis.urgency}")
print(f"Sentiment: {analysis.sentiment}")
print(f"Category: {analysis.category}")
```

### Example 2: Generate a Response

```python
# First analyze (from Example 1)
analysis = await agent.analyze_email(...)

# Then generate response
draft = await agent.generate_response(
    message=message,
    conversation_context=[],
    analysis=analysis,
    user_email="you@company.com",
    user_name="Your Name"
)

# Use the draft
print(f"Subject: {draft.subject}")
print(f"Body:\n{draft.body}")
print(f"Action: {draft.suggested_action}")
```

### Example 3: Complete Pipeline with Auto-Execution Decision

```python
from app.models.user import AutonomyLevel
from app.models.policy import Policy

# 1. Analyze
analysis = await agent.analyze_email(
    message=message,
    conversation_context=previous_messages,
    user_email="you@company.com",
    user_name="Your Name"
)

# 2. Generate response
draft = await agent.generate_response(
    message=message,
    conversation_context=previous_messages,
    analysis=analysis,
    user_email="you@company.com",
    user_name="Your Name"
)

# 3. Assess risk
risk = await agent.assess_risk(
    message=message,
    analysis=analysis,
    policies=[],  # Your user policies
    conversation_context=previous_messages
)

# 4. Calculate confidence
confidence = await agent.calculate_confidence(
    message=message,
    analysis=analysis,
    draft=draft,
    conversation_context=previous_messages,
    user_historical_acceptance_rate=0.85  # 85% acceptance rate
)

# 5. Decide on auto-execution
should_auto_execute = await agent.should_auto_execute(
    confidence=confidence,
    risk_level=risk.risk_level,
    autonomy_level=AutonomyLevel.MEDIUM,
    action_type=draft.suggested_action
)

# 6. Take action
if should_auto_execute:
    print("Auto-executing: Sending email")
    # await send_email(draft)
else:
    print("Presenting to user for review")
    # await create_pending_action(draft)
```

## FastAPI Integration

### Step 1: Add Dependency

```python
from fastapi import APIRouter, Depends
from app.services import get_agent_service, AgentService

router = APIRouter()

@router.post("/analyze/{conversation_id}")
async def analyze_email(
    conversation_id: UUID,
    agent: AgentService = Depends(get_agent_service)
):
    # Use agent service
    analysis = await agent.analyze_email(...)
    return {"analysis": analysis.model_dump()}
```

### Step 2: Register Router

```python
# In main.py or app.py
from app.api.routes import agent as agent_routes

app.include_router(agent_routes.router)
```

## Common Patterns

### Pattern: Processing Incoming Email

```python
async def process_incoming_email(message: Message, user: User):
    """Complete email processing workflow."""

    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)

    # Get conversation context
    context = await get_conversation_messages(message.conversation_id)

    # Get user policies
    policies = await get_user_policies(user.id)

    # Process
    analysis = await agent.analyze_email(
        message, context, user.email, user.name
    )

    # Check if actionable
    if not analysis.is_actionable:
        return {"action": "no_response_needed"}

    # Generate draft
    draft = await agent.generate_response(
        message, context, analysis, user.email, user.name
    )

    # Assess and decide
    risk = await agent.assess_risk(message, analysis, policies, context)
    confidence = await agent.calculate_confidence(
        message, analysis, draft, context
    )

    should_auto = await agent.should_auto_execute(
        confidence, risk.risk_level, user.autonomy_level, draft.suggested_action
    )

    # Create action record
    action = await create_agent_action(
        conversation_id=message.conversation_id,
        draft=draft,
        confidence=confidence,
        risk=risk.risk_level,
        auto_execute=should_auto
    )

    return {
        "action_id": action.id,
        "auto_execute": should_auto,
        "draft": draft.body
    }
```

### Pattern: Testing Policies

```python
async def test_policy_against_email(policy: Policy, message: Message):
    """Test if a policy matches an email."""

    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)

    # Analyze email first
    analysis = await agent.analyze_email(
        message, [], "test@company.com", "Test User"
    )

    # Check policy match
    matches = await agent.evaluate_policies(
        message, analysis, [policy]
    )

    if matches:
        match = matches[0]
        print(f"Policy matched with {match.confidence:.0%} confidence")
        print(f"Reason: {match.reasoning}")
        return True
    else:
        print("Policy did not match")
        return False
```

### Pattern: Batch Processing

```python
async def process_multiple_emails(messages: list[Message], user: User):
    """Process multiple emails efficiently."""

    import asyncio

    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)

    # Process all emails in parallel
    tasks = [
        agent.analyze_email(msg, [], user.email, user.name)
        for msg in messages
    ]

    analyses = await asyncio.gather(*tasks)

    return [
        {
            "message_id": msg.id,
            "intent": analysis.intent.primary,
            "urgency": analysis.urgency
        }
        for msg, analysis in zip(messages, analyses)
    ]
```

## Error Handling

### Handle API Errors

```python
import anthropic
from fastapi import HTTPException

try:
    analysis = await agent.analyze_email(...)
except anthropic.APIError as e:
    # API error (rate limit, auth, etc.)
    raise HTTPException(
        status_code=503,
        detail=f"AI service error: {str(e)}"
    )
except Exception as e:
    # Other errors
    raise HTTPException(
        status_code=500,
        detail="Internal server error"
    )
```

### Validate Results

```python
analysis = await agent.analyze_email(...)

# Check for spam before processing
if analysis.is_likely_spam:
    return {"action": "moved_to_spam"}

# Check urgency
if analysis.urgency == "critical":
    await notify_user_immediately()
```

## Testing

### Unit Test

```python
import pytest
from app.services import AgentService

@pytest.mark.asyncio
async def test_confidence_calculation():
    agent = AgentService(api_key="test-key")

    confidence = await agent.calculate_confidence(
        message=test_message,
        analysis=test_analysis,
        draft=test_draft,
        conversation_context=[]
    )

    assert 0 <= confidence <= 100
```

### Integration Test (requires API key)

```python
import pytest
import os

@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_email_analysis():
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        pytest.skip("API key not set")

    agent = AgentService(api_key=api_key)

    analysis = await agent.analyze_email(
        message=real_message,
        conversation_context=[],
        user_email="test@company.com",
        user_name="Test User"
    )

    assert analysis.intent is not None
    assert analysis.category is not None
```

## Configuration

### Customize Model Settings

```python
class CustomAgentService(AgentService):
    MODEL_NAME = "claude-opus-4-5-20251101"
    MAX_TOKENS = 8192  # Increase for longer responses
    TEMPERATURE = 0.8  # More creative

agent = CustomAgentService(api_key=api_key)
```

### User Preferences

```python
# Pass preferences to response generation
user_prefs = {
    "communication_tone": "formal",
    "response_length": "detailed",
    "include_greeting": True,
    "signature": "Best regards,\nSarah Chen\nProduct Manager"
}

draft = await agent.generate_response(
    message=message,
    conversation_context=context,
    analysis=analysis,
    user_email=user.email,
    user_name=user.name,
    user_preferences=user_prefs
)
```

## Next Steps

1. **Read Full Documentation**: See `AGENT_SERVICE_README.md`
2. **Review Examples**: Check `agent_example.py`
3. **Study API Integration**: See `api_integration_example.py`
4. **Run Tests**: `pytest app/services/test_agent.py -v`
5. **Customize Prompts**: Review `PROMPTS_REFERENCE.md`

## Common Questions

### Q: How much does it cost per email?
**A**: Approximately $0.05-0.15 per email with full analysis and response generation.

### Q: How fast is it?
**A**: 2-4 seconds for analysis, 3-5 seconds for response generation. Total ~7-13 seconds for complete pipeline.

### Q: Can I use a different Claude model?
**A**: Yes, change `MODEL_NAME` in the service. However, Opus 4.5 is recommended for best quality.

### Q: Is my email data stored?
**A**: No. Anthropic does not store or train on your data when using the API.

### Q: What happens if the API is down?
**A**: The service will raise an `anthropic.APIError`. Implement retry logic and fallbacks.

### Q: Can I run this locally?
**A**: Yes, just set your `ANTHROPIC_API_KEY` environment variable.

### Q: How do I improve confidence scores?
**A**: Provide more conversation context, ensure good historical acceptance rates, and use clear email communication.

## Support

- **Documentation**: `AGENT_SERVICE_README.md`
- **Examples**: `agent_example.py`
- **Tests**: `test_agent.py`
- **Prompts**: `PROMPTS_REFERENCE.md`

Happy automating!
