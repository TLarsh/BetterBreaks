

from celery import shared_task
from django.utils import timezone
from ..models.break_execution import BreakExecution
from ..services.notification_service import NotificationService


@shared_task
def send_break_reminders():
    now = timezone.now()

    upcoming = BreakExecution.objects.filter(
        status="approved",
        recommended_start__lte=now + timezone.timedelta(minutes=15),
        recommended_start__gte=now,
    )

    for br in upcoming:
        NotificationService.notify(
            user=br.user,
            event="break_reminder",
            title="Upcoming break ⏳",
            message="Your break starts in 15 minutes.",
            metadata={"break_id": str(br.id)},
        )
