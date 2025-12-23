from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from ..models.break_execution import BreakExecution
from ..services.break_lifecycle_service import BreakLifecycleService
from ..services.user_metrics_service import UserMetricsService
from ..services.optimization_service import OptimizationService
from ..services.notification_service import NotificationService


# celery task

def send_break_reminders():
    tomorrow = timezone.now().date() + timedelta(days=1)

    upcoming = BreakExecution.objects.filter(
        status="approved",
        recommended_start=tomorrow,
    )

    for br in upcoming:
        NotificationService.notify(
            user=br.user,
            event="break_reminder",
            title="Upcoming break ⏰",
            message="You have a planned break starting tomorrow. Get ready!",
            metadata={
                "start": br.recommended_start.isoformat(),
                "end": br.recommended_end.isoformat(),
            },
        )



@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3},
)
def process_break_completion_async(self, break_execution_id):
    """
    Handles the FULL lifecycle when a break is taken:
    - BreakScore
    - StreakScore
    - OptimizationScore
    - UserMetrics refresh
    """

    break_exec = BreakExecution.objects.select_related("user").get(
        id=break_execution_id
    )

    # Idempotency guard
    if break_exec.status != "taken":
        return f"Break {break_exec.id} ignored (status={break_exec.status})"

    with transaction.atomic():
        # 1️⃣ Core scoring + streaks + optimization
        BreakLifecycleService.process_break_completion(break_exec)

        # 2️⃣ Rebuild metrics (stress, sleep, work hours)
        UserMetricsService.build(break_exec.user)

    return f"Break {break_exec.id} processed successfully"


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3},
)
def process_missed_break_async(self, break_execution_id):
    """
    Processes a missed break:
    - Marks as missed
    - Penalizes optimization score
    - Refreshes metrics
    """

    break_exec = BreakExecution.objects.select_related("user").get(
        id=break_execution_id
    )

    # Idempotency guard
    if break_exec.status == "missed":
        return f"Break {break_exec.id} already missed"

    with transaction.atomic():
        break_exec.status = "missed"
        break_exec.missed_at = timezone.now()
        break_exec.save(update_fields=["status", "missed_at"])

        # Penalize optimization
        OptimizationService.calculate_daily_optimization(
            break_exec.user,
            break_exec.recommended_start.date()
        )

        # Rebuild metrics (stress ↑)
        UserMetricsService.build(break_exec.user)

    return f"Break {break_exec.id} marked as missed"


@shared_task(bind=True)
def process_all_missed_breaks(self):
    """
    Finds all overdue approved breaks and processes them as missed.
    """

    now = timezone.now()

    overdue_breaks = BreakExecution.objects.filter(
        status="approved",
        recommended_end__lt=now
    ).values_list("id", flat=True)

    for break_id in overdue_breaks:
        process_missed_break_async.delay(break_id)

    return f"{len(overdue_breaks)} missed breaks queued"
