from django.contrib import admin
from django.utils import timezone
from django.utils.text import Truncator

from core.models.event_models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "category",
        "location",
        "start_date",
        "end_date",
        "price",
        "capacity",
        "created_at",
    )
    list_filter = ("category", "start_date", "created_at")
    search_fields = ("title", "description", "location")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-start_date",)
    date_hierarchy = "start_date"

    actions = ("delete_past_events",)

    def id(self, obj):
        return str(obj.pk)[:8]
    id.short_description = "ID"

    def short_description(self, obj):
        return Truncator(obj.description or "").chars(120)
    short_description.short_description = "Description"

    @admin.action(description="Delete all selected events that have already ended")
    def delete_past_events(self, request, queryset):
        cutoff = timezone.now()
        past_qs = queryset.filter(end_date__lt=cutoff)
        count = past_qs.count()
        past_qs.delete()
        self.message_user(request, f"Deleted {count} past event(s).")