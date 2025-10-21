from django.contrib import admin
from ..models.settings_models import UserSettings

# Custom Admin Configuration for UserSettings Model
@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "theme",
        "language",
        "timezone",
        "currency"
    )
    search_fields = ("user__full_name",)
    ordering = ("user__full_name",)