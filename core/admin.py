from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User,
    Client,
    LastLogin,
    DateEntry,
    BlackoutDate,
    WellbeingScore,
    UserSettings,
    ActionData,
    OnboardingData,
)

# Custom Admin Configuration for User Model
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_active", "date_joined")
    search_fields = ("username", "email", "first_name", "last_name")
    fieldsets = [
        (
            "Personal Info",
            {
                "fields": [
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "profile_picture_path",
                ]
            },
        ),
        (
            "Preferences",
            {
                "fields": [
                    "holiday_days",
                    "birthday",
                    "home_location_timezone",
                    "home_location_coordinates",
                    "working_days_per_week",
                ]
            },
        ),
        (
            "Account Status",
            {"fields": ["is_active", "is_staff", "date_joined"]},
        ),
    ]
    readonly_fields = ["date_joined"]
    ordering = ("-date_joined",)

# Custom Admin Configuration for LastLogin Model
class LastLoginAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "login_date",
        "ip_address",
        "client",
        "token_valid",
    )
    list_filter = ("client", "token_valid", "login_date")
    search_fields = ("user__username", "ip_address")
    readonly_fields = ("token", "login_date")
    ordering = ("-login_date",)

# Custom Admin Configuration for DateEntry Model
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
class BlackoutDateAdmin(admin.ModelAdmin):
    list_display = ("user", "start_date", "end_date")
    list_filter = ("start_date", "end_date")
    search_fields = ("user__username",)
    date_hierarchy = "start_date"
    ordering = ("start_date",)

# Custom Admin Configuration for WellbeingScore Model
class WellbeingScoreAdmin(admin.ModelAdmin):
    list_display = ("user", "score", "score_date")
    list_filter = ("score_date",)
    search_fields = ("user__username",)
    date_hierarchy = "score_date"
    ordering = ("-score_date",)

# Custom Admin Configuration for Client Model
class ClientAdmin(admin.ModelAdmin):
    list_display = ("client_name", "client_description", "enabled")
    list_filter = ("enabled",)
    search_fields = ("client_name", "client_description")
    ordering = ("client_name",)

# Custom Admin Configuration for ActionData Model
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

# Custom Admin Configuration for OnboardingData Model
class OnboardingDataAdmin(admin.ModelAdmin):
    list_display = ("user", "survey_completion_date")
    list_filter = ("survey_completion_date",)
    search_fields = ("user__username",)
    date_hierarchy = "survey_completion_date"
    ordering = ("-survey_completion_date",)

# Custom Admin Configuration for UserSettings Model
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "theme",
        "language",
        "timezone",
        "currency"
    )
    search_fields = ("user__username",)
    ordering = ("user__username",)

# Register all models with custom configurations
admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(LastLogin, LastLoginAdmin)
admin.site.register(DateEntry, DateEntryAdmin)
admin.site.register(BlackoutDate, BlackoutDateAdmin)
admin.site.register(WellbeingScore, WellbeingScoreAdmin)
admin.site.register(ActionData, ActionDataAdmin)
admin.site.register(OnboardingData, OnboardingDataAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)