from django.contrib import admin
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from core.models.payment_models import Payment
from core.models.booking_models import Booking


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "short_id",
        "booking_reference",
        "user_email",
        "reference",
        "amount",
        "status",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("reference", "booking__id", "booking__event__title", "booking__user__email")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("booking",)

    actions = ("mark_as_success", "mark_as_failed", "mark_as_pending", "delete_older_than_365_days")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("booking", "booking__user", "booking__event")

    def short_id(self, obj):
        return str(obj.pk)[:8]
    short_id.short_description = "ID"

    def booking_reference(self, obj):
        return getattr(obj.booking, "id", "")
    booking_reference.short_description = "Booking"

    def user_email(self, obj):
        return getattr(getattr(obj.booking, "user", None), "email", "")
    user_email.short_description = "User"
    user_email.admin_order_field = "booking__user__email"

    @admin.action(description="Mark selected payments as SUCCESS and mark bookings PAID")
    def mark_as_success(self, request, queryset):
        updated_payments = 0
        updated_bookings = 0
        with transaction.atomic():
            for p in queryset.exclude(status=Payment.Status.SUCCESS):
                p.status = Payment.Status.SUCCESS
                p.save(update_fields=["status"])
                updated_payments += 1
                try:
                    booking = p.booking
                    if booking.status != Booking.Status.PAID:
                        booking.status = Booking.Status.PAID
                        booking.save(update_fields=["status"])
                        updated_bookings += 1
                except Exception:
                    continue
        self.message_user(request, f"Marked {updated_payments} payment(s) SUCCESS and {updated_bookings} booking(s) PAID.")

    @admin.action(description="Mark selected payments as FAILED and mark bookings FAILED")
    def mark_as_failed(self, request, queryset):
        updated_payments = 0
        updated_bookings = 0
        with transaction.atomic():
            for p in queryset.exclude(status=Payment.Status.FAILED):
                p.status = Payment.Status.FAILED
                p.save(update_fields=["status"])
                updated_payments += 1
                try:
                    booking = p.booking
                    if booking.status != Booking.Status.FAILED:
                        booking.status = Booking.Status.FAILED
                        booking.save(update_fields=["status"])
                        updated_bookings += 1
                except Exception:
                    continue
        self.message_user(request, f"Marked {updated_payments} payment(s) FAILED and {updated_bookings} booking(s) FAILED.")

    @admin.action(description="Mark selected payments as PENDING")
    def mark_as_pending(self, request, queryset):
        updated = queryset.exclude(status=Payment.Status.PENDING).update(status=Payment.Status.PENDING)
        self.message_user(request, f"Marked {updated} payment(s) as PENDING.")

    @admin.action(description="Delete payments older than 365 days")
    def delete_older_than_365_days(self, request, queryset):
        cutoff = timezone.now() - timedelta(days=365)
        old_qs = queryset.filter(created_at__lt=cutoff)
        count = old_qs.count()
        old_qs.delete()
        self.message_user(request, f"Deleted {count} payment(s) older than 365 days.")
