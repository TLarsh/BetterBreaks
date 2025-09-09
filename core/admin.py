from django.contrib import admin
from django.utils.html import format_html
from .models import (
    User,
    Client,
    LastLogin,
    DateEntry,
    BlackoutDate,
    # WellbeingScore,
    UserSettings,
    ActionData,
    # OnboardingData,
    UserNotificationPreference,
    BreakPlan,
    LeaveBalance,
    BreakPreferences,
)

# Custom Admin Configuration for User Model
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "is_active",
        "date_joined",
    )
    list_filter = ("is_active", "date_joined")
    search_fields = ("full_name", "email")
    fieldsets = [
        (
            "Personal Info",
            {
                "fields": [
                    "full_name",
                    "email",
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
# class WellbeingScoreAdmin(admin.ModelAdmin):
#     list_display = ("user", "score", "score_date")
#     list_filter = ("score_date",)
#     search_fields = ("user__username",)
#     date_hierarchy = "score_date"
#     ordering = ("-score_date",)

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

# Custom Admin Configuration for BreakPlan Model
@admin.register(BreakPlan)
class BreakPlanAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'type',
        'status',
        'startDate',
        'endDate',
        'created_at',
    )
    list_filter = ('type', 'status', 'startDate')
    search_fields = ('user__username', 'description', 'type', 'status')
    ordering = ('-created_at',)

    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Break Plan Info', {
            'fields': ('user', 'type', 'status', 'startDate', 'endDate', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

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

# custom admin configuration for LeaveBalance Model
@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("anual_leave_balance", "already_used_balance", "anual_leave_refresh_date", "updated_at")
    readonly_fields = ("updated_at",)
    search_fields = ("anual_leave_balance",)

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

# Register all models with custom configurations
admin.site.register(User, UserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(LastLogin, LastLoginAdmin)
admin.site.register(DateEntry, DateEntryAdmin)
admin.site.register(BlackoutDate, BlackoutDateAdmin)
# admin.site.register(WellbeingScore, WellbeingScoreAdmin)
admin.site.register(ActionData, ActionDataAdmin)
# admin.site.register(OnboardingData, OnboardingDataAdmin)
admin.site.register(UserSettings, UserSettingsAdmin)
# admin.site.register(UserNotificationPreference, UserNotificationPreferenceAdmin)