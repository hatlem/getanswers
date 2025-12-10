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
