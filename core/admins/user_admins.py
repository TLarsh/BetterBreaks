from django.contrib import admin
from django.utils.html import format_html
from core.models.user_models import (User, LastLogin)


# Custom Admin Configuration for User Model
@admin.register(User)
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
@admin.register(LastLogin)
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


# admin.site.register(User)