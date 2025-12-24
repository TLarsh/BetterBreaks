import logging
from typing import Optional

from django.conf import settings
from django.utils import timezone

from ..models.preference_models import UserNotificationPreference
from ..models.notification_models import Notification
from ..models.user_models import User
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
        user,
        event,
        title,
        message,
        metadata=None,
    ) -> None:

        prefs = NotificationService._get_preferences(user)

        if not prefs:
            logger.info(f"No preferences for user {user.id}")
            return

        if not NotificationService._event_allowed(event, prefs):
            return

        # SYSTEM notification (always)
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
                NotificationService._send_push(user, title, message, metadata)

            # EMAIL
            if prefs.emailEnabled:
                NotificationService._send_email(user, title, message)

            notification.mark_sent()

        except Exception as e:
            notification.mark_failed(str(e))

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
    # Channels
    # ============================

    @staticmethod
    def _send_push(user, title, message, metadata=None):
        """
        Push notification handler (Firebase / OneSignal / Expo).
        """
        try:
            if not getattr(user, "fcmToken", None):
                return

            logger.info(f"📲 Push → {user.email}: {title}")

            # 🔌 Example (pseudo)
            # push_client.send(
            #   token=user.fcmToken,
            #   title=title,
            #   body=message,
            #   data=metadata or {}
            # )

        except Exception as e:
            logger.error(f"Push notification failed for user {user.id}: {e}")

    @staticmethod
    def _send_email(user, title, message):
        """
        Email notification handler.
        """
        try:
            if not user.email:
                return

            logger.info(f"📧 Email → {user.email}: {title}")

            # 🔌 Example (pseudo)
            # send_mail(
            #   subject=title,
            #   message=message,
            #   from_email=settings.DEFAULT_FROM_EMAIL,
            #   recipient_list=[user.email],
            # )

        except Exception as e:
            logger.error(f"Email notification failed for user {user.id}: {e}")

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


