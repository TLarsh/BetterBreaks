# from django.contrib import admin
# from core.models.onboarding_models import OnboardingData

# # Custom Admin Configuration for OnboardingData Model
# @admin.register(OnboardingData)
# class OnboardingDataAdmin(admin.ModelAdmin):
#     list_display = ("user", "survey_completion_date")
#     list_filter = ("survey_completion_date",)
#     search_fields = ("user__username",)
#     date_hierarchy = "survey_completion_date"
#     ordering = ("-survey_completion_date",)