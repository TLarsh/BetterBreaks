from django.contrib import admin
from core.models.break_models import (
    BreakPlan,
    BreakSuggestion,
)


# Custom Admin Configuration for BreakSuggestion Model
@admin.register(BreakSuggestion)
class BreakSuggestionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "title",
        "start_date",
        "end_date",
        "priority",
        "is_accepted",
        "created_at",
        "updated_at",
    )
    list_filter = ("priority", "is_accepted", "start_date", "end_date", "based_on_mood", "based_on_workload", "based_on_preferences", "based_on_weather")
    search_fields = ("user__email", "title", "description", "reason")
    date_hierarchy = "start_date"
    ordering = ("-priority", "-created_at")
    autocomplete_fields = ("user",)
    readonly_fields = ("created_at", "updated_at")


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
