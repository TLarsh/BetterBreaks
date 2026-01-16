import logging
from typing import Optional

from django.utils import timezone

from ..models.preference_models import UserNotificationPreference
from ..models.notification_models import Notification
from ..models.user_models import User

from ..utils.email_utils import send_notification_email
from ..utils.firebase_utils import send_firebase_push
from django.shortcuts import get_object_or_404
logger = logging.getLogger(__name__)


class NotificationService:
    """
    Central notification dispatcher.
    Handles preferences, channels, and delivery.
    """

    # ============================
    # Public API
    # ============================

    @staticmethod
    def notify(
        *,
        user: User,
        event: str,
        title: str,
        message: str,
        metadata: Optional[dict] = None,
    ) -> None:

        prefs = NotificationService._get_preferences(user)

        if not prefs:
            logger.info(f"No preferences for user {user.id}")
            return

        if not NotificationService._event_allowed(event, prefs):
            return

        # SYSTEM notification (always stored)
        notification = Notification.objects.create(
            user=user,
            event=event,
            title=title,
            message=message,
            metadata=metadata or {},
            channel="system",
            status="pending",
        )

        try:
            # PUSH
            if prefs.pushEnabled:
                send_firebase_push(
                    token=getattr(user, "fcmToken", None),
                    title=title,
                    body=message,
                    data=metadata,
                )

            # EMAIL
            if prefs.emailEnabled:
                send_notification_email(
                    email=user.email,
                    title=title,
                    message=message,
                )

            notification.mark_sent()

        except Exception as e:
            notification.mark_failed(str(e))
            logger.error(f"Notification failed for user {user.id}: {e}")

    # ============================
    # Event rules
    # ============================

    @staticmethod
    def _event_allowed(event: str, prefs: UserNotificationPreference) -> bool:
        mapping = {
            "break_reminder": prefs.breaksReminder,
            "break_suggested": prefs.suggestions,
            "break_deadline": prefs.deadlineAlerts,
            "break_missed": prefs.deadlineAlerts,
            "weekly_digest": prefs.weeklyDigest,
        }
        return mapping.get(event, False)

    # ============================
    # Internals
    # ============================

    @staticmethod
    def _get_preferences(user) -> Optional[UserNotificationPreference]:
        try:
            return user.notification_preferences
        except UserNotificationPreference.DoesNotExist:
            return None







class NotificationCRUDService:

    @staticmethod
    def list_for_user(user):
        return Notification.objects.filter(user=user)

    @staticmethod
    def get_and_mark_read(user, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=user
        )
        notification.mark_read()
        return notification

    @staticmethod
    def mark_all_read(user):
        Notification.objects.filter(
            user=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )

    @staticmethod
    def delete(user, notification_id):
        Notification.objects.filter(
            id=notification_id,
            user=user
        ).delete()


