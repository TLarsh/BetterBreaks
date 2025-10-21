from django.contrib import admin
from core.models.date_models import (
    DateEntry,
    BlackoutDate,
)
# Custom Admin Configuration for DateEntry Model
@admin.register(DateEntry)
class DateEntryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "start_date",
        "end_date",
        "recurring_event_expression",
    )
    list_filter = ("start_date", "end_date")
    search_fields = ("title", "description", "user__username")
    date_hierarchy = "start_date"
    ordering = ("start_date",)


# Custom Admin Configuration for BlackoutDate Model
@admin.register(BlackoutDate)
class BlackoutDateAdmin(admin.ModelAdmin):
    list_display = ("user", "start_date", "end_date")
    list_filter = ("start_date", "end_date")
    search_fields = ("user__username",)
    date_hierarchy = "start_date"
    ordering = ("start_date",)