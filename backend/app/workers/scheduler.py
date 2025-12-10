"""Celery Beat scheduler configuration for periodic tasks."""

from celery.schedules import crontab
from app.workers.celery import celery_app

# Configure periodic task schedule
celery_app.conf.beat_schedule = {
    # Sync all users' emails every 5 minutes
    "sync-all-users-every-5-minutes": {
        "task": "app.workers.tasks.sync_emails.sync_all_users",
        "schedule": 300.0,  # 5 minutes in seconds
    },

    # Cleanup expired magic links daily at 3 AM
    "cleanup-expired-magic-links-daily": {
        "task": "app.workers.tasks.cleanup.cleanup_magic_links",
        "schedule": crontab(hour=3, minute=0),  # 3:00 AM daily
    },

    # Cleanup old actions weekly on Sunday at 4 AM
    "cleanup-old-actions-weekly": {
        "task": "app.workers.tasks.cleanup.cleanup_old_actions",
        "schedule": crontab(hour=4, minute=0, day_of_week=0),  # Sunday 4:00 AM
    },

    # Send daily digests at 8 AM
    "send-daily-digests": {
        "task": "app.workers.tasks.notifications.send_daily_digests_all",
        "schedule": crontab(hour=8, minute=0),  # 8:00 AM daily
    },
}

# Optional: Configure timezone for crontab schedules
celery_app.conf.timezone = "UTC"
