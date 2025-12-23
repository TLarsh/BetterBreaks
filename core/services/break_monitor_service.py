# services/break_monitor_service.py

from django.utils import timezone
from ..models.break_execution import BreakExecution
from .break_lifecycle_service import BreakLifecycleService


def mark_missed_breaks():
    today = timezone.now().date()

    missed = BreakExecution.objects.filter(
        status="approved",
        recommended_end__lt=today,
        processed_at__isnull=True,
    )

    for br in missed:
        br.status = "missed"
        br.save(update_fields=["status"])

        BreakLifecycleService.process_break_missed(br)
