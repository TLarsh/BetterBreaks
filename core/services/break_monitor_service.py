# services/break_monitor.py

from django.utils import timezone
from ..models.break_execution import BreakExecution
from .optimization_service import OptimizationService


def mark_missed_breaks():
    today = timezone.now().date()

    missed = BreakExecution.objects.filter(
        status="approved",
        recommended_end__lt=today
    )

    for br in missed:
        br.status = "missed"
        br.save()

        OptimizationService.calculate_daily_optimization(
            br.user,
            br.recommended_start
        )
