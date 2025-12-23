# services/break_reminder_service.py

from django.utils import timezone
from datetime import timedelta

from ..models.break_execution import BreakExecution
from .notification_service import NotificationService
from core.constants.notification_events import BREAK_REMINDER


def send_break_reminders():
    tomorrow = timezone.now().date() + timedelta(days=1)

    upcoming = BreakExecution.objects.filter(
        status="approved",
        recommended_start=tomorrow,
        processed_at__isnull=True,
    )

    for br in upcoming:
        NotificationService.notify(
            user=br.user,
            event=BREAK_REMINDER,
            title="Upcoming break ⏰",
            message="You have a planned break starting tomorrow. Get ready!",
            metadata={
                "start": br.recommended_start.isoformat(),
                "end": br.recommended_end.isoformat(),
            },
        )
    