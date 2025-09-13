import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lifestyle_backend.settings")

app = Celery("lifestyle_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Celery Beat schedule
app.conf.beat_schedule = {
    "refresh-holidays-every-month": {
        "task": "holidays.tasks.refresh_all_user_holidays",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),  # every 1st day of month
    },
}
