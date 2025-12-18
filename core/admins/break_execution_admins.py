from django.contrib import admin
from django.utils import timezone

from core.models.break_execution import BreakExecution


@admin.register(BreakExecution)
class BreakExecutionAdmin(admin.ModelAdmin):
    list_display = (
        "short_id",
        "user",
        "status",
        "recommended_start",
        "recommended_end",
        "actual_start",
        "actual_end",
        "optimisation_score",
        "created_at",
    )
    list_filter = ("status", "recommended_start", "recommended_end", "created_at")
    search_fields = ("user__email", "user__username")
    readonly_fields = ("id", "created_at", "optimisation_score")
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    autocomplete_fields = ("user",)

    actions = ("mark_as_taken", "mark_as_missed", "reset_to_recommended")

    def short_id(self, obj):
        return str(obj.id)[:8]
    short_id.short_description = "ID"

    @admin.action(description="Mark selected executions as Taken (set actual dates if empty)")
    def mark_as_taken(self, request, queryset):
        updated = 0
        for obj in queryset:
            if obj.status != "taken":
                if not obj.actual_start:
                    obj.actual_start = obj.recommended_start
                if not obj.actual_end:
                    obj.actual_end = obj.recommended_end
                obj.status = "taken"
                obj.save(update_fields=["actual_start", "actual_end", "status"])
                updated += 1
        self.message_user(request, f"Marked {updated} execution(s) as taken.")

    @admin.action(description="Mark selected executions as Missed")
    def mark_as_missed(self, request, queryset):
        updated = queryset.exclude(status="missed").update(status="missed")
        self.message_user(request, f"Marked {updated} execution(s) as missed.")

    @admin.action(description="Reset selected executions to Recommended (clears actual dates)")
    def reset_to_recommended(self, request, queryset):
        updated = 0
        for obj in queryset:
            obj.actual_start = None
            obj.actual_end = None
            obj.status = "recommended"
            obj.save(update_fields=["actual_start", "actual_end", "status"])
            updated += 1
        self.message_user(request, f"Reset {updated} execution(s) to recommended.")

