from django.contrib import admin
from ..models.action_data_models import ActionData


# Custom Admin Configuration for ActionData Model
@admin.register(ActionData)
class ActionDataAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action_date",
        "application_area_name",
        "action_duration_seconds",
    )
    list_filter = ("action_date", "application_area_name")
    search_fields = ("user__username", "action_description")
    date_hierarchy = "action_date"
    ordering = ("-action_date",)