# Claude AI Agent Service

A comprehensive AI-powered email processing service that acts as an intelligent executive assistant, capable of analyzing emails, generating human-like responses, assessing risks, and making autonomous decisions based on user preferences.

## Overview

The `AgentService` leverages Anthropic's Claude Opus 4.5 model to provide:

- **Email Analysis**: Deep understanding of intent, sentiment, urgency, and context
- **Response Generation**: Human-like, contextually appropriate email responses
- **Risk Assessment**: Intelligent evaluation of potential risks and implications
- **Policy Matching**: Automated rule-based decision making
- **Confidence Scoring**: Multi-factor confidence calculation for autonomous actions
- **Auto-Execution Logic**: Smart determination of when to act autonomously vs. seek approval

## Key Features

### 1. Comprehensive Email Analysis

The service provides detailed analysis including:

- **Intent Detection**: Primary and secondary intents (request, question, FYI, invitation, etc.)
- **Sentiment Analysis**: Overall sentiment and communication tone
- **Urgency Assessment**: Critical, high, medium, or low urgency levels
- **Category Classification**: Meeting, task, question, update, sales, support, etc.
- **Entity Extraction**: Key information like dates, amounts, people, organizations
- **Spam Detection**: Identification of suspicious or spam content
- **Relationship Assessment**: Colleague, client, vendor, unknown

### 2. Intelligent Response Generation

The service generates responses that:

- Match the tone and formality of incoming emails
- Reflect the user's natural communication style
- Address all points raised in the email
- Maintain professional relationships
- Sound natural and human, not robotic
- Include appropriate greetings and closings
- Are concise yet complete

### 3. Advanced Risk Assessment

Risk evaluation considers:

- **Financial Implications**: Payments, contracts, pricing commitments
- **Legal Implications**: Agreements, obligations, liability, compliance
- **Confidential Content**: Sensitive data, private information, trade secrets
- **Unknown Parties**: New contacts, unverified senders
- **Reputational Risk**: Public statements, controversial topics
- **Operational Risk**: System access, process changes

### 4. Smart Confidence Scoring

Confidence scores (0-100) are calculated based on:

- **Intent Clarity** (25 points): How clear the email's purpose is
- **Response Quality** (25 points): Quality of the generated response
- **Context Familiarity** (20 points): Familiarity with conversation and sender
- **Historical Performance** (20 points): User's past acceptance rate
- **Risk Adjustment** (10 points): Risk factors and safety considerations

### 5. Autonomous Decision Making

The service determines auto-execution based on:

| Autonomy Level | Risk Level | Confidence Threshold | Auto-Execute |
|---------------|------------|---------------------|--------------|
| HIGH          | LOW        | >= 70%              | Yes          |
| MEDIUM        | LOW        | >= 85%              | Yes          |
| LOW           | Any        | N/A                 | No           |
| Any           | MEDIUM/HIGH| N/A                 | No           |

Special rules:
- SEND actions require +10% confidence threshold
- HIGH/MEDIUM risk always requires approval
- Critical urgency may lower threshold by 5%

## Usage Examples

### Basic Email Analysis

```python
from app.services import AgentService
from app.core.config import settings

# Initialize the service
agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)

# Analyze an email
analysis = await agent.analyze_email(
    message=incoming_message,
    conversation_context=previous_messages,
    user_email="user@company.com",
    user_name="User Name"
)

print(f"Intent: {analysis.intent.primary}")
print(f"Urgency: {analysis.urgency}")
print(f"Category: {analysis.category}")
```

### Generate Response

```python
# Generate a response draft
draft = await agent.generate_response(
    message=incoming_message,
    conversation_context=previous_messages,
    analysis=analysis,
    user_email="user@company.com",
    user_name="User Name",
    user_preferences={
        "communication_tone": "professional-friendly",
        "response_length": "concise"
    }
)

print(f"Subject: {draft.subject}")
print(f"Body: {draft.body}")
print(f"Suggested action: {draft.suggested_action}")
```

### Assess Risk

```python
# Assess risk level
risk = await agent.assess_risk(
    message=incoming_message,
    analysis=analysis,
    policies=user_policies,
    conversation_context=previous_messages
)

print(f"Risk level: {risk.risk_level}")
print(f"Risk factors: {risk.risk_factors}")
```

### Complete Processing Pipeline

```python
# 1. Analyze
analysis = await agent.analyze_email(message, context, user_email, user_name)

# 2. Generate response
draft = await agent.generate_response(message, context, analysis, user_email, user_name)

# 3. Assess risk
risk = await agent.assess_risk(message, analysis, policies, context)

# 4. Evaluate policies
policy_matches = await agent.evaluate_policies(message, analysis, policies)

# 5. Calculate confidence
confidence = await agent.calculate_confidence(
    message, analysis, draft, context,
    user_historical_acceptance_rate=0.85
)

# 6. Decide on auto-execution
should_auto_execute = await agent.should_auto_execute(
    confidence=confidence,
    risk_level=risk.risk_level,
    autonomy_level=AutonomyLevel.MEDIUM,
    action_type=draft.suggested_action
)

if should_auto_execute:
    # Send the email automatically
    await send_email(draft)
else:
    # Present to user for review
    await create_agent_action(draft, confidence, risk.risk_level)
```

## Data Models

### EmailAnalysis

```python
class EmailAnalysis(BaseModel):
    intent: EmailIntent
    sentiment: str  # positive, neutral, negative, urgent
    tone: str  # formal, casual, friendly, demanding, etc.
    urgency: str  # critical, high, medium, low
    requires_immediate_response: bool
    category: str  # meeting, task, question, update, etc.
    is_actionable: bool
    extracted_entities: list[ExtractedEntity]
    key_points: list[str]
    sender_relationship: str  # colleague, client, vendor, unknown
    is_likely_spam: bool
    context_summary: str
```

### DraftResponse

```python
class DraftResponse(BaseModel):
    subject: str
    body: str
    suggested_action: ActionType  # DRAFT, SEND, FILE, SCHEDULE, TRIAGE
    reasoning: str
    alternative_tone: Optional[str]
    key_considerations: list[str]
```

### RiskAssessment

```python
class RiskAssessment(BaseModel):
    risk_level: RiskLevel  # LOW, MEDIUM, HIGH
    risk_factors: list[str]
    mitigation_suggestions: list[str]
    has_financial_implications: bool
    has_legal_implications: bool
    has_confidential_content: bool
    involves_unknown_party: bool
```

### PolicyMatch

```python
class PolicyMatch(BaseModel):
    policy_id: UUID
    policy_name: str
    matched_rule: str
    confidence: float  # 0-1
    action_override: Optional[str]
    reasoning: str
```

## System Prompts

The service uses carefully crafted system prompts that instruct Claude to:

### Analysis Prompt
- Act as an expert executive assistant
- Provide objective, precise analysis
- Consider cultural and professional context
- Flag unusual or concerning content
- Recognize VIP senders and urgent matters
- Understand conversation threading

### Response Generation Prompt
- Write natural, human-like emails
- Match tone and formality of incoming email
- Be concise but complete
- Use proper email etiquette
- Maintain professional reputation
- Sound like the user, not a robot
- Handle formal and casual communication appropriately

### Risk Assessment Prompt
- Evaluate financial, legal, and reputational risks
- Be conservative but not paranoid
- Focus on material risks, not theoretical possibilities
- Consider operational and security implications
- Provide actionable mitigation suggestions

### Policy Evaluation Prompt
- Match emails against user-defined rules
- Use both literal and semantic matching
- Assign accurate confidence scores
- Explain why policies match
- Use common sense for intent-based rules

## Configuration

The service uses the following configuration:

```python
MODEL_NAME = "claude-opus-4-5-20251101"  # Latest Claude model
MAX_TOKENS = 4096
TEMPERATURE = 0.7  # Balanced creativity and consistency
```

For risk assessment, a lower temperature (0.3) is used for more consistent evaluation.

## Integration Points

### With Database Models

The service integrates seamlessly with:

- `Message` - Email messages
- `Conversation` - Email threads
- `Policy` - User automation rules
- `User` - User preferences and autonomy levels
- `AgentAction` - Audit log of AI actions

### With API Endpoints

Typical integration in API routes:

```python
@router.post("/conversations/{conversation_id}/process")
async def process_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    agent: AgentService = Depends(get_agent_service)
):
    # Get conversation and messages
    conversation = await get_conversation(db, conversation_id, current_user.id)
    messages = await get_messages(db, conversation_id)

    # Get latest incoming message
    latest_message = messages[-1]

    # Get user policies
    policies = await get_user_policies(db, current_user.id)

    # Process with agent
    analysis = await agent.analyze_email(
        latest_message, messages[:-1],
        current_user.email, current_user.name
    )

    draft = await agent.generate_response(
        latest_message, messages[:-1], analysis,
        current_user.email, current_user.name
    )

    risk = await agent.assess_risk(
        latest_message, analysis, policies, messages[:-1]
    )

    confidence = await agent.calculate_confidence(
        latest_message, analysis, draft, messages[:-1]
    )

    should_auto_execute = await agent.should_auto_execute(
        confidence, risk.risk_level,
        current_user.autonomy_level,
        draft.suggested_action
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

    return {
        "analysis": analysis,
        "draft": draft,
        "risk": risk,
        "confidence": confidence,
        "auto_execute": should_auto_execute,
        "action_id": action.id
    }
```

## Error Handling

The service handles errors gracefully:

```python
try:
    analysis = await agent.analyze_email(...)
except anthropic.APIError as e:
    # Handle API errors (rate limits, auth issues, etc.)
    logger.error(f"Claude API error: {e}")
    raise HTTPException(status_code=503, detail="AI service unavailable")
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Agent service error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

## Performance Considerations

- **Concurrent Processing**: Use `asyncio.gather()` for parallel processing of multiple emails
- **Caching**: Consider caching analysis results for similar emails
- **Token Usage**: Monitor token consumption for cost optimization
- **Rate Limiting**: Implement rate limiting for API calls
- **Timeouts**: Set appropriate timeouts for Claude API calls

## Testing

See `agent_example.py` for comprehensive usage examples including:

- Complete email processing pipeline
- Urgent email handling
- Spam detection
- Policy matching
- Risk assessment

Run examples:
```bash
python -m app.services.agent_example
```

## Future Enhancements

Potential improvements:

1. **Learning from User Feedback**: Adapt based on user edits and rejections
2. **Multi-language Support**: Handle emails in different languages
3. **Attachment Analysis**: Process and understand email attachments
4. **Calendar Integration**: Smart scheduling and meeting management
5. **CRM Integration**: Leverage customer relationship data
6. **Template Learning**: Learn from user's frequently used responses
7. **Batch Processing**: Process multiple emails efficiently
8. **Real-time Suggestions**: Provide suggestions as user types

## Security Considerations

- API keys are loaded from environment variables
- User data is not logged or stored by Claude
- All communication with Claude API is encrypted (HTTPS)
- Sensitive data can be filtered before sending to Claude
- Audit logs track all AI actions for compliance

## Support

For issues or questions:
- Check the examples in `agent_example.py`
- Review the comprehensive docstrings in `agent.py`
- Consult the Anthropic Claude API documentation
- Contact the development team

## License

Part of the GetAnswers project.
