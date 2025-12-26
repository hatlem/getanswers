"""Celery configuration for GetAnswers background tasks."""

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "getanswers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.workers.tasks.sync_emails",
        "app.workers.tasks.process_email",
        "app.workers.tasks.notifications",
        "app.workers.tasks.cleanup",
        "app.workers.tasks.ai_learning",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    worker_prefetch_multiplier=1,  # Fair task distribution
)

# Celery Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    # AI Learning: Refresh stale writing profiles daily at 2 AM UTC
    "refresh-stale-writing-profiles": {
        "task": "refresh_stale_writing_profiles",
        "schedule": 86400.0,  # Every 24 hours
        "options": {"expires": 3600},
    },
    # AI Learning: Auto-analyze new edits weekly on Sundays at 3 AM UTC
    "auto-analyze-new-edits": {
        "task": "auto_analyze_new_edits",
        "schedule": 604800.0,  # Every 7 days
        "options": {"expires": 3600},
    },
}
