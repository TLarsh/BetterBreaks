from django.contrib import admin
from core.models.holiday_models import (
    PublicHoliday,
    PublicHolidayCalendar,
)

# Custom Admin Configuration for PublicHolidayCalendar Model
@admin.register(PublicHolidayCalendar)
class PublicHolidayCalendarAdmin(admin.ModelAdmin):
    list_display = ("user", "country_code", "is_enabled", "last_synced")
    list_filter = ("is_enabled", "country_code")
    search_fields = ("user__email", "country_code")
    ordering = ("user__email",)
    autocomplete_fields = ("user",)
    readonly_fields = ("last_synced",)


# Custom Admin Configuration for PublicHoliday Model
@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display = ("name", "date", "country_code", "calendar")
    list_filter = ("country_code", "date")
    search_fields = ("name", "calendar__user__email")
    ordering = ("-date",)
    date_hierarchy = "date"
    autocomplete_fields = ("calendar",)