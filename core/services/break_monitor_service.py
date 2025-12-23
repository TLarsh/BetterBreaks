# services/break_monitor_service.py

from django.utils import timezone
from ..models.break_execution import BreakExecution
from .break_lifecycle_service import BreakLifecycleService
from .optimization_service import OptimizationService
from .notification_service import NotificationService

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

        # 🔔 Notification
        NotificationService.notify(
            user=br.user,
            event="break_missed",
            title="You missed a break 😕",
            message="You missed a planned break. Try rescheduling to avoid burnout.",
            metadata={
                "break_id": str(br.id),
                "recommended_start": br.recommended_start.isoformat(),
            },
        )
