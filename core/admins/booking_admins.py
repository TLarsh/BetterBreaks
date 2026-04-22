from django.contrib import admin
from django.utils import timezone
from django.utils.text import Truncator

from core.models.booking_models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "short_id",
        "user_email",
        "event_title",
        "tickets",
        "total_amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__email", "user__username", "event__title")
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("user", "event")

    actions = ("mark_as_paid", "mark_as_failed", "delete_old_bookings")

    def short_id(self, obj):
        return str(obj.id)[:8]
    short_id.short_description = "ID"

    def user_email(self, obj):
        return getattr(obj.user, "email", "")
    user_email.short_description = "User"
    user_email.admin_order_field = "user__email"

    def event_title(self, obj):
        return getattr(obj.event, "title", "")
    event_title.short_description = "Event"
    event_title.admin_order_field = "event__title"

    @admin.action(description="Mark selected bookings as PAID")
    def mark_as_paid(self, request, queryset):
        updated = queryset.exclude(status=Booking.Status.PAID).update(status=Booking.Status.PAID)
        self.message_user(request, f"Marked {updated} booking(s) as PAID.")

    @admin.action(description="Mark selected bookings as FAILED")
    def mark_as_failed(self, request, queryset):
        updated = queryset.exclude(status=Booking.Status.FAILED).update(status=Booking.Status.FAILED)
        self.message_user(request, f"Marked {updated} booking(s) as FAILED.")

    @admin.action(description="Delete bookings older than 365 days")
    def delete_old_bookings(self, request, queryset):
        cutoff = timezone.now() - timezone.timedelta(days=365)
        old_qs = queryset.filter(created_at__lt=cutoff)
        count = old_qs.count()
        old_qs.delete()
        self.message_user(request, f"Deleted {count} booking(s) older than 365 days.")