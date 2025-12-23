# services/break_lifecycle_service.py

from django.db import transaction
from django.utils import timezone

from .break_score_service import BreakScoreService
from .streak_service import StreakService
from .optimization_service import OptimizationService
from .notification_service import NotificationService

from ..constants.notification_events import (
    BREAK_TAKEN,
    BREAK_MISSED,
)

class BreakLifecycleService:

    @staticmethod
    @transaction.atomic
    def process_break_completion(break_exec):
        if break_exec.status != "taken":
            return

        if break_exec.processed_at:
            return  # idempotency

        break_date = break_exec.actual_start.date()

        # Gamification
        BreakScoreService.score_break(break_exec)
        StreakService.update_streak(break_exec.user, break_date)
        OptimizationService.calculate_daily_optimization(
            break_exec.user, break_date
        )

        # Notification
        NotificationService.notify(
            user=break_exec.user,
            event=BREAK_TAKEN,
            title="Break completed 🎉",
            message="Nice work! Taking breaks helps your productivity and wellbeing.",
            metadata={
                "break_id": str(break_exec.id),
                "start": break_exec.actual_start.isoformat(),
                "end": break_exec.actual_end.isoformat() if break_exec.actual_end else None,
                "date": break_date.isoformat(),
            },
        )

        break_exec.processed_at = timezone.now()
        break_exec.save(update_fields=["processed_at"])

    @staticmethod
    @transaction.atomic
    def process_break_missed(break_exec):
        if break_exec.status != "missed":
            return

        if break_exec.processed_at:
            return

        OptimizationService.calculate_daily_optimization(
            break_exec.user,
            break_exec.recommended_start
        )

        NotificationService.notify(
            user=break_exec.user,
            event=BREAK_MISSED,
            title="You missed a break 😕",
            message="Skipping breaks can impact your wellbeing. Let’s plan the next one better.",
            metadata={
                "break_id": str(break_exec.id),
                "recommended_start": break_exec.recommended_start.isoformat(),
                "recommended_end": break_exec.recommended_end.isoformat(),
            },
        )

        break_exec.processed_at = timezone.now()
        break_exec.save(update_fields=["processed_at"])
