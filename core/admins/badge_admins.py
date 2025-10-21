from django.contrib import admin
from core.models.badge_models import Badge

# Custom Admin Configuration for Badge Model
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "badge_type",
        "earned_date",
        "description",
        "requirements_met",
        "created_at",
        "updated_at",
    )
    list_filter = ("badge_type", "earned_date", "created_at")
    search_fields = ("user__email", "badge_type", "description")
    readonly_fields = ("created_at", "updated_at", "earned_date")
    autocomplete_fields = ("user",)