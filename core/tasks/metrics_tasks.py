from celery import shared_task
from django.contrib.auth import get_user_model

from ..services.user_metrics_service import UserMetricsService
import logging

logger = logging.getLogger(__name__)

User = get_user_model()




@shared_task
def refresh_all_user_metrics():
    User = get_user_model()
    user_ids = User.objects.values_list("id", flat=True)

    logger.info(f"🚀 Scheduling metrics refresh for {len(user_ids)} users")

    for user_id in user_ids:
        refresh_user_metrics.delay(str(user_id))


# @shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
# def refresh_user_metrics(self, user_id):
#     # from django.contrib.auth import get_user_model
#     # User = get_user_model()

#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         logger.warning(f"Skipping metrics refresh — user {user_id} not found")
#         return "USER_NOT_FOUND"

#     UserMetricsService.build(user)
#     return "OK"

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3})
def refresh_user_metrics(self):
    for user in User.objects.all():
        UserMetricsService.build(user)

    return "Metrics refreshed"


