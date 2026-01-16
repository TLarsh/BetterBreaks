

from celery import shared_task
from django.utils import timezone
from ..models.break_execution import BreakExecution
from ..services.notification_service import NotificationService
from django.contrib.auth import get_user_model
User = get_user_model()


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


@shared_task
def send_weekly_digest():
    users = User.objects.filter(
        notification_preferences__weeklyDigest=True
    )

    for user in users:
        NotificationService.notify(
            user=user,
            event="weekly_digest",
            title="Your Weekly Break Summary 📊",
            message="Here's how you did with breaks this week!",
        )