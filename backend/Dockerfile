FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Environment variable to control worker vs API server
ENV RUN_WORKER=false

# Run the application (API server or Celery worker)
# Set RUN_WORKER=true to run as Celery worker
# Set RUN_BEAT=true to run as Celery beat scheduler
# Migrations run before starting the API server
CMD ["sh", "-c", "if [ \"$RUN_WORKER\" = 'true' ]; then celery -A app.workers.celery:celery_app worker --loglevel=info; elif [ \"$RUN_BEAT\" = 'true' ]; then celery -A app.workers.celery:celery_app beat --loglevel=info; else alembic upgrade head || alembic stamp head; uvicorn app.main:app --host 0.0.0.0 --port 8000; fi"]
