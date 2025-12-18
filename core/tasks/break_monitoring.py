from celery import shared_task
from django.utils import timezone
from datetime import timedelta

from ..models.break_execution import BreakExecution
from ..services.break_lifecycle_service import BreakLifecycleService
from ..services.optimization_service import OptimizationService


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 10})
def mark_missed_breaks(self):
    today = timezone.now()

    missed_breaks = BreakExecution.objects.filter(
        status="approved",
        recommended_end__lt=today
    )

    for br in missed_breaks:
        br.status = "missed"
        br.save(update_fields=["status"])

        OptimizationService.calculate_daily_optimization(
            br.user,
            br.recommended_start.date()
        )

    return missed_breaks.count()
