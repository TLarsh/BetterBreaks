from django.contrib import admin
from ..models.recommendation_models import UserMetrics, BreakRecommendation


@admin.register(UserMetrics)
class UserMetricsAdmin(admin.ModelAdmin):
    list_display = (
        'user_email', 'work_hours_per_week', 'stress_level', 'sleep_quality',
        'prefers_travel', 'season_preference', 'break_type_preference',
        'created_at', 'updated_at',
    )
    search_fields = ('user__email',)
    list_filter = (
        'season_preference',
        'break_type_preference',
        'prefers_travel',
        'stress_level',
        'sleep_quality',
    )
    readonly_fields = ('created_at', 'updated_at')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'


@admin.register(BreakRecommendation)
class BreakRecommendationAdmin(admin.ModelAdmin):
    list_display = (
        'user_email', 'recommended_start_date', 'recommended_end_date',
        'predicted_length_days', 'recommended_season',
        'is_viewed', 'is_accepted', 'created_at',
    )
    list_filter = (
        'recommended_season',
        'is_viewed',
        'is_accepted',
        'created_at',
    )
    search_fields = ('user__email', 'message')
    readonly_fields = ('created_at',)
    actions = ['mark_as_viewed', 'mark_as_accepted', 'mark_as_rejected']

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'

    @admin.action(description="Mark selected as viewed")
    def mark_as_viewed(self, request, queryset):
        queryset.update(is_viewed=True)

    @admin.action(description="Mark selected as accepted")
    def mark_as_accepted(self, request, queryset):
        queryset.update(is_accepted=True)

    @admin.action(description="Mark selected as rejected")
    def mark_as_rejected(self, request, queryset):
        queryset.update(is_accepted=False)
