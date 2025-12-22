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
        "task": "core.tasks.refresh_all_user_holidays",
        "schedule": crontab(day_of_month=1, hour=0, minute=0),  # every 1st day of month
    },
    "generate-recommendations-weekly": {
        "task": "core.tasks.recommendation_tasks.generate_recommendations_for_all_users",
        "schedule": crontab(day_of_week=1, hour=1, minute=0),  # every Monday at 1:00 AM
    },


    "mark-missed-breaks-daily": {
        "task": "app.tasks.break_monitoring.mark_missed_breaks",
        "schedule": crontab(hour=1, minute=0),
    },
    "refresh-all-user-metrics-daily": {
        "task": "core.tasks.metrics_tasks.refresh_all_user_metrics",
        "schedule": crontab(hour=2, minute=0),
    },
    # "refresh-user-metrics-nightly": {
    #     "task": "app.tasks.metrics_tasks.refresh_user_metrics",
    #     "schedule": crontab(hour=2, minute=0),
    # },
    "daily-optimization-snapshot": {
        "task": "app.tasks.optimization_tasks.recalculate_daily_optimization",
        "schedule": crontab(hour=3, minute=0),
    },
}
