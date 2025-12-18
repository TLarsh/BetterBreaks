from celery import shared_task
from django.utils import timezone

from ..models.score_models import OptimizationScore
from ..services.optimization_service import OptimizationService


@shared_task(bind=True)
def recalculate_daily_optimization():
    today = timezone.now().date()

    users = OptimizationScore.objects.values_list("user_id", flat=True).distinct()

    for user_id in users:
        OptimizationService.calculate_daily_optimization(
            user_id,
            today
        )

    return "Daily optimization recalculated"
