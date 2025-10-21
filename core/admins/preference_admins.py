from django.contrib import admin
from core.models.preference_models import (
    UserNotificationPreference,
    BreakPreferences
)

# Custom Admin Configuration for UserNotificationPrefrence Model
@admin.register(UserNotificationPreference)
class UserNotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'breaksReminder',
        'suggestions',
        'deadlineAlerts',
        'weeklyDigest',
        'pushEnabled',
        'emailEnabled',
    )
    list_filter = ('breaksReminder', 'suggestions', 'deadlineAlerts', 'weeklyDigest', 'pushEnabled', 'emailEnabled')
    search_fields = ('user__email', 'user__username')



# Custom Admin Configuration for BreakPreferences Model
@admin.register(BreakPreferences)
class BreakPreferencesAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "preference",
        "weather_based_recommendation",
        "to_be_confirmed",
    )
    list_filter = (
        "preference",
        "weather_based_recommendation",
        "to_be_confirmed",
    )
    search_fields = (
        "user__full_name",
        "user__email",
    )
    ordering = ("user",)
    autocomplete_fields = ("user",)
    list_editable = ("weather_based_recommendation", "to_be_confirmed")
    fieldsets = (
        (None, {
            "fields": ("user", "preference"),
        }),
        ("Additional Options", {
            "fields": ("weather_based_recommendation", "to_be_confirmed"),
            "classes": ("collapse",),
        }),
    )