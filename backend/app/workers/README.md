# GetAnswers Background Workers

This directory contains Celery workers for background task processing in GetAnswers.

## Architecture

- **celery.py**: Main Celery application configuration
- **scheduler.py**: Celery Beat schedule for periodic tasks
- **tasks/**: Individual task modules organized by functionality
  - **sync_emails.py**: Email synchronization with Gmail
  - **process_email.py**: AI email processing pipeline
  - **notifications.py**: User notifications and digests
  - **cleanup.py**: Database maintenance tasks

## Running Workers

### Local Development

1. Make sure Redis is running:
```bash
redis-server
```

2. Run the Celery worker:
```bash
# From backend directory
celery -A app.workers.celery worker --loglevel=info

# Or use the convenience script
python celery_worker.py
```

3. Run the Celery Beat scheduler (for periodic tasks):
```bash
celery -A app.workers.celery beat --loglevel=info
```

### Docker Deployment

The Dockerfile supports running as worker or scheduler via environment variables:

```bash
# Run as API server (default)
docker run -e RUN_WORKER=false myapp

# Run as Celery worker
docker run -e RUN_WORKER=true myapp

# Run as Celery Beat scheduler
docker run -e RUN_BEAT=true myapp
```

## Tasks Overview

### Email Synchronization
- `sync_user_emails(user_id)`: Sync emails for a single user
- `sync_all_users()`: Periodic task to sync all users (runs every 5 minutes)

### Email Processing
- `process_single_email(message_id)`: Process email through AI pipeline
- `batch_process_emails(message_ids)`: Process multiple emails in batch

### Notifications
- `send_action_notification(user_id, action_id)`: Notify user about high-risk actions
- `send_daily_digest(user_id)`: Send daily activity digest to user
- `send_daily_digests_all()`: Periodic task to send digests to all users (8 AM daily)

### Cleanup
- `cleanup_magic_links()`: Delete expired/used magic links (3 AM daily)
- `cleanup_old_actions()`: Archive old resolved actions (4 AM Sunday)

## Scheduled Tasks

| Task | Schedule | Description |
|------|----------|-------------|
| sync_all_users | Every 5 minutes | Sync emails for all connected users |
| cleanup_magic_links | Daily at 3 AM | Remove expired and old magic links |
| cleanup_old_actions | Weekly (Sun 4 AM) | Archive resolved actions older than 90 days |
| send_daily_digests_all | Daily at 8 AM | Send activity digests to all users |

## Configuration

Worker configuration is in `celery.py`:
- Task time limit: 5 minutes
- Serializer: JSON
- Timezone: UTC
- Fair task distribution enabled

## Database Sessions

All tasks properly manage async database sessions:
- Create new session per task
- Automatic commit on success
- Automatic rollback on error
- Proper cleanup in finally block

## Error Handling

Tasks include retry logic:
- Email sync: 3 retries with exponential backoff (60s, 120s, 240s)
- Email processing: 3 retries with exponential backoff (30s, 60s, 120s)
- Notifications: No automatic retry (fail fast)
- Cleanup: No automatic retry (will run again on next schedule)

## Monitoring

View worker status:
```bash
celery -A app.workers.celery inspect active
celery -A app.workers.celery inspect stats
```

View scheduled tasks:
```bash
celery -A app.workers.celery inspect scheduled
```

## Development Notes

- Tasks use asyncio.run() to execute async code in sync Celery context
- Each task creates its own database session
- Logging configured for all tasks
- TODO comments mark integration points with services to be implemented
