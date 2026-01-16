from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Notification(models.Model):
   

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("failed", "Failed"),
    )

    CHANNEL_CHOICES = (
        ("push", "Push"),
        ("email", "Email"),
        ("system", "System"),
    )

    EVENT_CHOICES = (
        ("break_suggested", "Break Suggested"),
        ("break_reminder", "Break Reminder"),
        ("break_taken", "Break Taken"),
        ("break_missed", "Break Missed"),
        ("break_deadline", "Break Deadline"),
        ("weekly_digest", "Weekly Digest"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    event = models.CharField(max_length=50, choices=EVENT_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()

    channel = models.CharField(
        max_length=20,
        choices=CHANNEL_CHOICES,
        default="system",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "event"]),
            models.Index(fields=["status"]),
            models.Index(fields=["user", "is_read"]), 
        ]

    def __str__(self):
        return f"{self.user.email} | {self.event} | {self.status}"

    # =========================
    # Delivery lifecycle
    # =========================

    def mark_sent(self):
        self.status = "sent"
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at"])

    def mark_failed(self, error: str):
        self.status = "failed"
        self.error_message = error
        self.save(update_fields=["status", "error_message"])

    # =========================
    # User interaction
    # =========================

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
