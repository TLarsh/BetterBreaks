from django.contrib import admin
from django.utils.text import Truncator
from django.utils import timezone
from datetime import timedelta

from core.models.notification_models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "short_id",
        "user_email",
        "event",
        "title",
        "short_message",
        "channel",
        "status",
        "is_read",
        "sent_at",
        "created_at",
    )
    list_filter = ("event", "channel", "status", "is_read", "created_at")
    search_fields = ("user__email", "title", "message", "error_message")
    readonly_fields = ("id", "sent_at", "created_at", "read_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("user",)

    actions = (
        "mark_as_read",
        "mark_as_unread",
        "mark_as_sent",
        "mark_as_failed",
        "resend_notifications",
        "delete_older_than_90_days",
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")

    def short_id(self, obj):
        return str(obj.id)[:8]
    short_id.short_description = "ID"

    def user_email(self, obj):
        return getattr(obj.user, "email", "")
    user_email.short_description = "User"

    def short_message(self, obj):
        return Truncator(obj.message or "").chars(120)
    short_message.short_description = "Message"

    @admin.action(description="Mark selected notifications as read")
    def mark_as_read(self, request, queryset):
        updated = 0
        for n in queryset.filter(is_read=False):
            n.mark_read()
            updated += 1
        self.message_user(request, f"Marked {updated} notification(s) as read.")

    @admin.action(description="Mark selected notifications as unread")
    def mark_as_unread(self, request, queryset):
        updated = queryset.filter(is_read=True).update(is_read=False, read_at=None)
        self.message_user(request, f"Marked {updated} notification(s) as unread.")

    @admin.action(description="Mark selected notifications as sent (set sent_at)")
    def mark_as_sent(self, request, queryset):
        updated = 0
        now = timezone.now()
        for n in queryset.exclude(status="sent"):
            n.status = "sent"
            n.sent_at = now
            n.save(update_fields=["status", "sent_at"])
            updated += 1
        self.message_user(request, f"Marked {updated} notification(s) as sent.")

    @admin.action(description="Mark selected notifications as failed (provide generic error)")
    def mark_as_failed(self, request, queryset):
        updated = 0
        for n in queryset.exclude(status="failed"):
            n.mark_failed("Marked as failed by admin")
            updated += 1
        self.message_user(request, f"Marked {updated} notification(s) as failed.")

    @admin.action(description="Resend selected notifications (set status to pending)")
    def resend_notifications(self, request, queryset):
        updated = queryset.update(status="pending", sent_at=None, error_message=None)
        self.message_user(request, f"Queued {updated} notification(s) for resend.")

    @admin.action(description="Delete notifications older than 90 days")
    def delete_older_than_90_days(self, request, queryset):
        cutoff = timezone.now() - timedelta(days=90)
        old_qs = queryset.filter(created_at__lt=cutoff)
        count = old_qs.count()
        old_qs.delete()
        self.message_user(request, f"Deleted {count} notification(s) older than 90 days.")