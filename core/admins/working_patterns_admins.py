# admin.py
from django.contrib import admin
from core.models.working_pattern_models import WorkingPattern


@admin.register(WorkingPattern)
class WorkingPatternAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "pattern_type",
        "created_at",
    )

    list_filter = (
        "pattern_type",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__username",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "shift_preview",
    )

    fieldsets = (
        (
            "General",
            {
                "fields": (
                    "user",
                    "pattern_type",
                    "created_at",
                )
            },
        ),
        (
            "Custom Working Pattern",
            {
                "fields": (
                    "custom_days",
                ),
                "classes": ("collapse",),
                "description": "Used only when pattern type is Custom.",
            },
        ),
        (
            "Shift Working Pattern",
            {
                "fields": (
                    "days_on",
                    "days_off",
                    "start_date",
                    "rotation_pattern",
                    "shift_preview",
                ),
                "classes": ("collapse",),
                "description": "Used only when pattern type is Shift.",
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        """
        Dynamically show relevant sections based on pattern type.
        """
        if obj:
            if obj.pattern_type == "custom":
                return (
                    self.fieldsets[0],
                    self.fieldsets[1],
                )
            elif obj.pattern_type == "shift":
                return (
                    self.fieldsets[0],
                    self.fieldsets[2],
                )
        return self.fieldsets

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pattern_type != "shift":
            return ("created_at",)
        return self.readonly_fields
