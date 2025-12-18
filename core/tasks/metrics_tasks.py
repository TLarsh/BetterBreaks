from celery import shared_task
from django.contrib.auth import get_user_model

from ..services.user_metrics_service import UserMetricsService

User = get_user_model()


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def refresh_user_metrics(self):
    for user in User.objects.all():
        UserMetricsService.build(user)

    return "Metrics refreshed"
