#!/usr/bin/env python
"""
Celery worker entry point for local development.

This script provides an easy way to run the Celery worker locally.

Usage:
    python celery_worker.py              # Run worker
    celery -A app.workers.celery worker  # Alternative via Celery CLI
    celery -A app.workers.celery beat    # Run scheduler
"""

from app.workers.celery import celery_app
from app.workers import scheduler  # Import to register beat schedule

if __name__ == "__main__":
    celery_app.start()
