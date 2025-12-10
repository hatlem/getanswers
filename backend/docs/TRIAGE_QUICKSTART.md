# Triage Service - Quick Start Guide

## Import and Initialize

```python
from app.services import TriageService, GmailService, AgentService
from app.core.database import get_db
from app.core.config import settings

# In an async function or FastAPI endpoint
async def process_emails(user_id: UUID, db: AsyncSession):
    # Initialize services
    gmail = GmailService()
    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)
    triage = TriageService(db, gmail, agent)

    # Use the service...
```

## Common Operations

### 1. Sync User's Inbox

```python
# Fetch and process recent emails
result = await triage.sync_user_inbox(
    user_id=user.id,
    max_messages=50  # Optional, default 50
)

print(f"Synced {result.processed} of {result.new_messages} emails")
print(f"Took {result.duration_seconds:.2f} seconds")

if result.errors:
    print(f"Errors: {result.error_details}")
```

### 2. Process a Single Email

```python
# Process one email (e.g., from webhook)
gmail_message = {
    'id': 'msg_123',
    'threadId': 'thread_456',
    'from': {'name': 'John', 'email': 'john@example.com'},
    'subject': 'Question about pricing',
    'body_text': 'What are your rates?',
    'body_html': '<p>What are your rates?</p>',
    'sent_at': datetime.utcnow()
}

result = await triage.process_new_email(
    user_id=user.id,
    gmail_message=gmail_message
)

print(f"Created action: {result.action_id}")
print(f"Confidence: {result.confidence}%")
print(f"Risk: {result.risk_level}")
print(f"Auto-executed: {result.auto_executed}")
```

### 3. Execute an Action

```python
# Execute an approved action
result = await triage.execute_action(
    action_id=action.id,
    auto_executed=False  # Set True if auto-executing
)

if result.success:
    print(f"Sent! Message ID: {result.gmail_message_id}")
else:
    print(f"Failed: {result.error}")
```

### 4. Group Message into Objective

```python
# Smart grouping (usually called internally)
objective = await triage.find_or_create_objective(
    user_id=user.id,
    message=message
)

print(f"Grouped into: {objective.title}")
```

### 5. Update Objective Status

```python
# Update status based on actions
await triage.update_objective_status(objective.id)

# Refresh to see new status
await db.refresh(objective)
print(f"Status: {objective.status}")
```

## FastAPI Integration

### Endpoint for Manual Sync

```python
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user

router = APIRouter(prefix="/triage", tags=["triage"])

@router.post("/sync")
async def sync_inbox(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Manually trigger inbox sync."""
    gmail = GmailService()
    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)
    triage = TriageService(db, gmail, agent)

    try:
        result = await triage.sync_user_inbox(user.id)
        return {
            "success": True,
            "processed": result.processed,
            "new_messages": result.new_messages,
            "errors": result.errors,
            "duration": result.duration_seconds
        }
    except Exception as e:
        raise HTTPException(500, detail=str(e))
```

### Endpoint for Action Execution

```python
@router.post("/actions/{action_id}/execute")
async def execute_action(
    action_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Execute an approved action."""
    # TODO: Verify action belongs to user

    gmail = GmailService()
    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)
    triage = TriageService(db, gmail, agent)

    result = await triage.execute_action(action_id)

    if not result.success:
        raise HTTPException(500, detail=result.error)

    return {
        "success": True,
        "message_id": result.gmail_message_id,
        "thread_id": result.gmail_thread_id
    }
```

## Celery Background Worker

### Task Definition

```python
# In app/workers/email_tasks.py
from celery import Celery
from app.core.database import AsyncSessionLocal

app = Celery('getanswers')

@app.task
async def sync_user_inbox_task(user_id: str):
    """Background task for inbox sync."""
    async with AsyncSessionLocal() as db:
        try:
            gmail = GmailService()
            agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)
            triage = TriageService(db, gmail, agent)

            result = await triage.sync_user_inbox(user_id)

            logger.info(
                f"Sync complete for user {user_id}: "
                f"{result.processed}/{result.new_messages} processed"
            )

            return {
                "user_id": user_id,
                "processed": result.processed,
                "errors": result.errors
            }

        except Exception as e:
            logger.error(f"Sync failed for user {user_id}: {e}")
            raise
```

### Schedule Periodic Syncs

```python
# In celery_config.py
from celery.schedules import crontab

beat_schedule = {
    'sync-all-inboxes': {
        'task': 'app.workers.sync_all_users',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    }
}

@app.task
async def sync_all_users():
    """Sync inbox for all active users."""
    async with AsyncSessionLocal() as db:
        users = await get_active_users(db)

        for user in users:
            sync_user_inbox_task.delay(str(user.id))
```

## Gmail Webhook Handler

```python
@router.post("/webhooks/gmail")
async def gmail_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Gmail push notification."""
    # Parse Pub/Sub message
    body = await request.json()
    message_data = body.get('message', {})

    # Decode notification
    import base64
    import json
    data = base64.b64decode(message_data['data']).decode('utf-8')
    notification = json.loads(data)

    user_email = notification['emailAddress']
    history_id = notification['historyId']

    # Find user
    user = await get_user_by_email(db, user_email)
    if not user:
        return {"status": "ignored"}

    # Fetch new messages
    gmail = GmailService()
    agent = AgentService(api_key=settings.ANTHROPIC_API_KEY)
    triage = TriageService(db, gmail, agent)

    # Sync inbox (will only process new messages)
    result = await triage.sync_user_inbox(user.id, max_messages=10)

    return {
        "status": "processed",
        "user_id": str(user.id),
        "processed": result.processed
    }
```

## Error Handling

### Try-Catch Pattern

```python
try:
    result = await triage.process_new_email(user.id, gmail_message)
except ValueError as e:
    # Validation error (bad message format)
    logger.error(f"Invalid message: {e}")
    raise HTTPException(400, detail=str(e))
except GmailServiceError as e:
    # Gmail API error
    logger.error(f"Gmail error: {e}")
    raise HTTPException(503, detail="Gmail service unavailable")
except Exception as e:
    # Unexpected error
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(500, detail="Internal server error")
```

### Graceful Degradation

```python
# Sync with error tolerance
result = await triage.sync_user_inbox(user.id, max_messages=100)

if result.errors > 0:
    logger.warning(
        f"Sync completed with {result.errors} errors: "
        f"{result.error_details}"
    )

    # Still return success if some messages processed
    if result.processed > 0:
        return {
            "success": True,
            "partial": True,
            "processed": result.processed,
            "errors": result.errors
        }
```

## Testing

### Unit Test Example

```python
import pytest
from app.services import TriageService

@pytest.mark.asyncio
async def test_process_email(db_session, test_user):
    """Test email processing."""
    gmail = GmailService()
    agent = AgentService(api_key="test_key")
    triage = TriageService(db_session, gmail, agent)

    gmail_message = {
        'id': 'msg_test',
        'threadId': 'thread_test',
        'from': {'name': 'Test', 'email': 'test@example.com'},
        'subject': 'Test',
        'body_text': 'Test body',
        'body_html': '<p>Test body</p>',
        'sent_at': datetime.utcnow()
    }

    result = await triage.process_new_email(test_user.id, gmail_message)

    assert result.action_id is not None
    assert 0 <= result.confidence <= 100
```

## Best Practices

### 1. Always Use Async Context

```python
# Good
async with AsyncSessionLocal() as db:
    triage = TriageService(db, gmail, agent)
    result = await triage.sync_user_inbox(user_id)

# Bad - don't reuse sessions across requests
triage = TriageService(global_db, gmail, agent)  # ❌
```

### 2. Handle Rate Limits

```python
# Add delays between operations
for user in users:
    await triage.sync_user_inbox(user.id)
    await asyncio.sleep(1)  # Rate limiting
```

### 3. Log Important Events

```python
import logging
logger = logging.getLogger(__name__)

result = await triage.process_new_email(user.id, message)

logger.info(
    f"Processed email {message['id']}: "
    f"action={result.action_id}, "
    f"confidence={result.confidence}, "
    f"auto_executed={result.auto_executed}"
)
```

### 4. Monitor Performance

```python
import time

start = time.time()
result = await triage.sync_user_inbox(user.id)
duration = time.time() - start

if duration > 60:  # More than 1 minute
    logger.warning(f"Slow sync for user {user.id}: {duration:.2f}s")
```

## Common Issues

### Issue: "User has no Gmail credentials"
**Solution:** Ensure user has completed OAuth flow:
```python
if not user.gmail_credentials:
    raise HTTPException(
        401,
        detail="Please connect your Gmail account first"
    )
```

### Issue: "Gmail API rate limit exceeded"
**Solution:** Add exponential backoff:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def sync_with_retry(user_id):
    return await triage.sync_user_inbox(user_id)
```

### Issue: "Database connection timeout"
**Solution:** Use connection pooling and increase timeouts:
```python
# In database.py
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30
)
```

## Performance Tips

1. **Use eager loading** for relationships:
   ```python
   # The service already does this internally
   .options(joinedload(Action.conversation).joinedload(Conversation.messages))
   ```

2. **Limit message context** to avoid memory issues:
   ```python
   # Default is 10 messages, adjust if needed
   context = await triage._get_conversation_context(conv_id, limit=5)
   ```

3. **Process in batches**:
   ```python
   # Sync smaller batches more frequently
   await triage.sync_user_inbox(user.id, max_messages=20)
   ```

4. **Cache user data** if processing many emails:
   ```python
   user = await triage._get_user(user_id)
   policies = await triage._get_active_policies(user_id)

   # Reuse for multiple messages (within same session)
   for message in messages:
       # Process using cached data
       pass
   ```

## See Also

- [Full Documentation](./TRIAGE_SERVICE.md) - Complete API reference
- [Implementation Details](./TRIAGE_IMPLEMENTATION.md) - Architecture overview
- [Test Suite](../tests/test_triage_service.py) - Example tests
