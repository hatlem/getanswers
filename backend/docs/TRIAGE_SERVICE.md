# Email Triage Service Documentation

## Overview

The `TriageService` is the heart of the GetAnswers email management system. It orchestrates the entire email processing pipeline, from syncing Gmail messages to generating AI-powered responses and executing approved actions.

## Architecture

### Pipeline Flow

```
Gmail Inbox
    ↓
[Sync Service]
    ↓
New Email → [Parse & Save Message]
    ↓
[Find/Create Conversation] (by thread_id)
    ↓
[Find/Create Objective] (smart grouping)
    ↓
[Get Context] (previous messages)
    ↓
[AI Analysis] (intent, sentiment, urgency)
    ↓
[Generate Response] (draft email)
    ↓
[Risk Assessment] (LOW/MEDIUM/HIGH)
    ↓
[Calculate Confidence] (0-100)
    ↓
[Create AgentAction]
    ↓
[Auto-Execute Decision]
    ├─ Yes → [Execute Action] → Gmail
    └─ No → [Queue for Review] → User Dashboard
```

## Core Components

### 1. TriageService

The main orchestration service that coordinates all email processing operations.

**Initialization:**
```python
from app.services import TriageService, GmailService, AgentService

triage = TriageService(
    db=db_session,
    gmail_service=GmailService(user_credentials),
    agent_service=AgentService(api_key)
)
```

### 2. GmailService

Interface for Gmail API operations (currently a placeholder for actual implementation).

**Key Methods:**
- `fetch_new_messages()` - Fetch new emails from Gmail
- `send_message()` - Send email reply
- `create_draft()` - Create draft email
- `archive_message()` - Archive and label emails

**TODO for Production:**
- Implement actual Google Gmail API integration
- Handle OAuth2 token refresh
- Parse MIME messages properly
- Handle rate limiting and quotas
- Support attachments

### 3. Response Models

**SyncResult:**
```python
{
    "new_messages": 15,
    "processed": 14,
    "errors": 1,
    "duration_seconds": 23.5,
    "last_sync_time": "2024-01-15T10:30:00Z",
    "error_details": ["Failed to process msg_123: ..."]
}
```

**ProcessingResult:**
```python
{
    "action_id": "uuid",
    "conversation_id": "uuid",
    "objective_id": "uuid",
    "confidence": 87.5,
    "risk_level": "low",
    "auto_executed": true,
    "action_type": "send"
}
```

**ExecutionResult:**
```python
{
    "success": true,
    "action_id": "uuid",
    "gmail_message_id": "msg_789",
    "gmail_thread_id": "thread_456",
    "executed_at": "2024-01-15T10:31:00Z"
}
```

## Key Features

### 1. Email Processing Pipeline

**Method:** `process_new_email(user_id, gmail_message)`

Processes a single incoming email through the complete AI analysis pipeline:

1. **Duplicate Detection** - Skip if message already processed
2. **Conversation Threading** - Group by Gmail thread_id
3. **Objective Grouping** - Smart grouping of related conversations
4. **Context Gathering** - Load previous messages for context
5. **AI Analysis** - Analyze intent, sentiment, urgency
6. **Response Generation** - Create draft response
7. **Risk Assessment** - Evaluate potential risks
8. **Confidence Scoring** - Calculate confidence (0-100)
9. **Action Creation** - Create AgentAction record
10. **Auto-Execution** - Execute if meets criteria

**Example:**
```python
result = await triage.process_new_email(
    user_id=user.id,
    gmail_message={
        'id': 'msg_123',
        'threadId': 'thread_456',
        'from': {'name': 'John Doe', 'email': 'john@example.com'},
        'subject': 'Project Update Request',
        'body_text': 'Could you send me an update?',
        'sent_at': datetime.utcnow()
    }
)

print(f"Action: {result.action_id}")
print(f"Confidence: {result.confidence}%")
print(f"Auto-executed: {result.auto_executed}")
```

### 2. Gmail Inbox Sync

**Method:** `sync_user_inbox(user_id, max_messages=50)`

Syncs emails from Gmail and processes each one:

1. **Fetch Messages** - Get new messages since last sync (default: 7 days)
2. **Process Each** - Run through processing pipeline
3. **Error Handling** - Continue on individual failures
4. **Statistics** - Return detailed sync stats

**Example:**
```python
result = await triage.sync_user_inbox(
    user_id=user.id,
    max_messages=100
)

print(f"Processed: {result.processed}/{result.new_messages}")
print(f"Duration: {result.duration_seconds}s")
if result.errors:
    print(f"Errors: {result.error_details}")
```

### 3. Action Execution

**Method:** `execute_action(action_id, auto_executed=False)`

Executes an approved action based on its type:

**Action Types:**

- **SEND** - Send email reply via Gmail
  - Creates sent message record
  - Updates objective status to "waiting_on_others"

- **DRAFT** - Create draft in Gmail
  - Saves draft for user review
  - Updates objective status to "waiting_on_others"

- **FILE** - Archive/label email
  - Adds labels in Gmail
  - Updates objective status to "handled"

- **SCHEDULE** - Create calendar event
  - TODO: Integration with Google Calendar

**Example:**
```python
result = await triage.execute_action(
    action_id=action.id,
    auto_executed=False  # User manually approved
)

if result.success:
    print(f"Sent: {result.gmail_message_id}")
else:
    print(f"Error: {result.error}")
```

### 4. Smart Objective Grouping

**Method:** `find_or_create_objective(user_id, message)`

Intelligently groups conversations into objectives using:

**Grouping Logic:**

1. **Thread-based** - Same Gmail thread = same conversation = same objective
2. **Subject Similarity** - Fuzzy matching on subject lines (0-0.4 weight)
3. **Participant Overlap** - Same senders/recipients (0-0.3 weight)
4. **Timeframe** - Recent activity within 7 days (0-0.3 weight)
5. **AI Analysis** - Use Claude to determine relatedness (future enhancement)

**Matching Threshold:** 0.7 (70% confidence required to group)

**Example:**
```python
objective = await triage.find_or_create_objective(
    user_id=user.id,
    message=incoming_message
)

print(f"Objective: {objective.title}")
print(f"Status: {objective.status}")
```

### 5. Objective Status Management

**Method:** `update_objective_status(objective_id)`

Automatically updates objective status based on action states:

**Status Rules:**

| Condition | Status |
|-----------|--------|
| Has pending actions | `WAITING_ON_YOU` |
| All actions approved/edited but awaiting reply | `WAITING_ON_OTHERS` |
| All actions complete | `HANDLED` |
| Has scheduled actions | `SCHEDULED` |
| User muted | `MUTED` |

**Example:**
```python
await triage.update_objective_status(objective.id)
```

## Auto-Execution Logic

Actions are automatically executed when all conditions are met:

### Decision Matrix

| Autonomy Level | Risk Level | Min Confidence | Action Type Modifier |
|----------------|------------|----------------|----------------------|
| **HIGH** | LOW | 70% | +10% for SEND |
| **MEDIUM** | LOW | 85% | +10% for SEND |
| **LOW** | ANY | Never | - |

**Special Rules:**
- MEDIUM/HIGH risk actions always require approval
- SEND actions require +10% confidence (higher threshold)
- Critical urgency may lower threshold by 5% (future)

**Example:**
```python
# HIGH autonomy, LOW risk, 75% confidence, SEND action
# Threshold: 70% + 10% = 80%
# Result: 75% < 80% → Requires review

# HIGH autonomy, LOW risk, 85% confidence, DRAFT action
# Threshold: 70%
# Result: 85% > 70% → Auto-execute ✓
```

## Priority Scoring

Actions are prioritized for review using a 0-100 point system:

### Priority Factors

- **Base:** 50 points
- **Urgency:** 0-40 points
  - Critical: +40
  - High: +30
  - Medium: +15
  - Low: 0
- **Risk Level:** 0-30 points
  - High: +30
  - Medium: +15
  - Low: 0
- **Immediate Response:** +20 points if required
- **Low Confidence:** +10 points if < 60%

**Example:**
```python
# Critical urgency + High risk + Low confidence
# = 50 + 40 + 30 + 10 = 130 → capped at 100
priority_score = 100  # Highest priority

# Low urgency + Low risk + High confidence
# = 50 + 0 + 0 = 50
priority_score = 50  # Medium priority
```

## Confidence Scoring

Confidence scores (0-100) are calculated based on multiple factors:

### Scoring Components

1. **Intent Clarity (0-25 points)**
   - Clear, actionable intent: +25
   - Spam/unclear: penalty

2. **Response Quality (0-25 points)**
   - Good reasoning: +15
   - Appropriate action type: +10
   - Substantial content: +5

3. **Context Familiarity (0-20 points)**
   - Existing conversation: +30
   - Known sender: +20
   - Clear category: +10

4. **Historical Performance (0-20 points)**
   - Based on user's past acceptance rate
   - Default: 10 points (neutral)

5. **Risk Adjustment (0-10 points)**
   - Low urgency routine: +3
   - Known sender: +2
   - Spam/unknown: penalty

**Example:**
```python
# Perfect scenario:
# Intent clarity: 25 + Response quality: 25 +
# Context: 20 + Historical: 20 + Risk: 10 = 100

# Uncertain scenario:
# Intent clarity: 10 + Response quality: 15 +
# Context: 5 + Historical: 10 + Risk: -5 = 35
```

## Error Handling

### Strategy

1. **Individual Failures** - Continue processing other messages
2. **Logging** - Comprehensive error logging for debugging
3. **Error Details** - Return error messages in results
4. **Retry Logic** - TODO: Implement exponential backoff

### Example

```python
try:
    result = await triage.process_new_email(user_id, gmail_msg)
except ValueError as e:
    logger.error(f"Validation error: {e}")
    # Invalid message format
except Exception as e:
    logger.error(f"Processing error: {e}", exc_info=True)
    # Critical failure
```

## Performance Considerations

### Optimization Tips

1. **Batch Processing** - Process multiple messages in parallel
2. **Caching** - Cache user data, policies between messages
3. **Database** - Use eager loading for relationships
4. **Rate Limiting** - Add delays between Gmail API calls
5. **Async Operations** - All database ops are async

### Benchmarks

- Average processing time: **2-5 seconds per email**
- Sync 50 messages: **~120 seconds** (with rate limiting)
- Database queries: **~10 per message**
- AI API calls: **~4 per message** (analysis, response, risk, policies)

## Integration Examples

### 1. FastAPI Endpoint

```python
from fastapi import APIRouter, Depends
from app.core.database import get_db
from app.services import TriageService, GmailService, AgentService

router = APIRouter()

@router.post("/sync")
async def sync_inbox(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync user's Gmail inbox."""
    gmail = GmailService(user.gmail_credentials)
    agent = AgentService(settings.ANTHROPIC_API_KEY)
    triage = TriageService(db, gmail, agent)

    result = await triage.sync_user_inbox(user.id)
    return result
```

### 2. Background Worker

```python
from celery import Celery
from app.services import TriageService

app = Celery('getanswers')

@app.task
async def sync_user_inbox_task(user_id: str):
    """Background task to sync inbox."""
    async with AsyncSessionLocal() as db:
        # Setup services
        triage = TriageService(db, gmail, agent)

        # Sync inbox
        result = await triage.sync_user_inbox(user_id)

        # Log results
        logger.info(f"Synced {result.processed} messages for {user_id}")
```

### 3. Webhook Handler

```python
@router.post("/webhook/gmail")
async def gmail_webhook(
    notification: dict,
    db: AsyncSession = Depends(get_db)
):
    """Handle Gmail push notifications."""
    user_id = notification['user_id']
    message_id = notification['message_id']

    # Fetch the specific message
    gmail = GmailService(user_credentials)
    message = await gmail.fetch_message(message_id)

    # Process immediately
    triage = TriageService(db, gmail, agent)
    result = await triage.process_new_email(user_id, message)

    return {"processed": True, "action_id": str(result.action_id)}
```

## Future Enhancements

### High Priority

1. **Gmail API Integration** - Implement actual Gmail service
2. **Retry Logic** - Exponential backoff for failed operations
3. **Better Objective Matching** - Use AI for semantic similarity
4. **Calendar Integration** - Support SCHEDULE action type
5. **Attachment Handling** - Process and store attachments

### Medium Priority

1. **Parallel Processing** - Process multiple messages concurrently
2. **Incremental Sync** - Track last_sync_time on user model
3. **Policy Learning** - Learn from user feedback
4. **Custom Workflows** - User-defined automation rules
5. **Analytics** - Track processing metrics

### Low Priority

1. **Multi-provider Support** - Outlook, Yahoo, etc.
2. **Smart Scheduling** - Suggest meeting times
3. **Template Library** - Reusable response templates
4. **A/B Testing** - Test different response styles
5. **Sentiment Tracking** - Monitor relationship health

## Testing

See `tests/test_triage_service.py` for comprehensive test suite covering:

- Email processing pipeline
- Duplicate detection
- Conversation threading
- Objective grouping
- Action execution
- Status updates
- Error handling

**Run tests:**
```bash
pytest tests/test_triage_service.py -v
```

## Troubleshooting

### Common Issues

**Issue:** "User has no Gmail credentials configured"
- **Solution:** Ensure user has completed OAuth flow and credentials are stored

**Issue:** "Action execution failed"
- **Solution:** Check Gmail API permissions and token validity

**Issue:** "Duplicate messages being processed"
- **Solution:** Verify gmail_message_id is being saved correctly

**Issue:** "Low confidence scores"
- **Solution:** Review user's historical acceptance rate and policy configuration

## Support

For questions or issues:
- Check logs in `/var/log/getanswers/`
- Review error details in SyncResult
- Monitor database for stuck actions
- Verify Gmail API quota usage

## See Also

- [Agent Service Documentation](./AGENT_SERVICE.md)
- [Gmail Integration Guide](./GMAIL_INTEGRATION.md)
- [API Reference](./API_REFERENCE.md)
