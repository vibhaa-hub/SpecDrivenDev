from celery import Celery
from celery.schedules import crontab
import os

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "expense_app",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Beat Schedule
celery_app.conf.beat_schedule = {
    "generate-recurring-transactions-daily": {
        "task": "app.services.recurring_service.generate_recurring_transactions",
        "schedule": crontab(hour=0, minute=0), # Every day at midnight
    },
}
