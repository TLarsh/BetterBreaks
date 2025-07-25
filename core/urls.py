from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    RequestOTPView,
    VerifyOTPView,
    ResetPasswordView,
    DateListView,
    BlackoutDatesView,
    ProfileView,
    UpdateWellbeingView,
    LogActionView,
    UpdateProfileView,
    UpdateSettingsView,
    GetSettingsView,
    GetOnboardingDataView,
    UpdateOnboardingDataView,
    FetchPublicHolidaysView,
    ListPublicHolidaysView,
    OptimizationScoreView,
    GamificationDataView,
    SuggestedDatesView,
    AddDateView,
    DeleteDateView,
    AddBlackoutDateView,
    DeleteBlackoutDateView,
    WellbeingQuestionView,
    CreateBreakPlanView,
    ListUserBreakPlansView,
    UpdateBreakPlanView,
    DeleteBreakPlanView,
    UserSettingsView,
)

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from .swagger_api_fe import schema_view
schema_view = get_schema_view(
    openapi.Info(
        title="BetterBreaks",
        default_version='v1',
        description="BetterBreaks Backend",
        terms_of_service="https://testing.betterbreaks.org",
        contact=openapi.Contact(email="support@betterbreaks.org"),
        license=openapi.License(name="Proprietary"),
    ),
    
    public=True,
    # url="http://127.0.0.1:8000//",
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/register/', RegisterView.as_view(), name='register'),  # Ensure 'register' matches test
    path('api/login/', LoginView.as_view(), name='login'),          # Ensure 'login' matches test
    path('api/logout/', LogoutView.as_view(), name='logout'),      # Ensure 'logout' matches test
    path('api/request-reset/', RequestOTPView.as_view()),
    path('api/verify-otp/', VerifyOTPView.as_view()),
    path('api/reset-password/', ResetPasswordView.as_view()),
    path('api/dates/', DateListView.as_view(), name='dates'),       # Ensure 'dates' matches test
    path('api/blackout-dates/', BlackoutDatesView.as_view(), name='blackout_dates'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    # path('api/update-wellbeing/', UpdateWellbeingView.as_view(), name='update_wellbeing'),
    path('api/log-action/', LogActionView.as_view(), name='log_action'),
    path('api/update-profile/', UpdateProfileView.as_view(), name='update_profile'),
    # path('api/update-settings/', UpdateSettingsView.as_view(), name='update_settings'),
    # path('api/settings/', GetSettingsView.as_view(), name='get_settings'),
    # path('api/onboarding/', GetOnboardingDataView.as_view(), name='get_onboarding_data'),
    # path('api/update-onboarding/', UpdateOnboardingDataView.as_view(), name='update_onboarding_data'),
    # path("fetch-public-holidays/", FetchPublicHolidaysView.as_view(), name="fetch-public-holidays"),
    # path("list-public-holidays/", ListPublicHolidaysView.as_view(), name="list-public-holidays"),
    path("optimization-score/", OptimizationScoreView.as_view(), name="optimization-score"),
    # path("gamification-data/", GamificationDataView.as_view(), name="gamification-data"),
    # path("suggested-dates/", SuggestedDatesView.as_view(), name="suggested-dates"),
    path("api/add-date/", AddDateView.as_view(), name="add-date"),



    path("api/breaks/plan", CreateBreakPlanView.as_view(), name="create-break-plan"),
    path("api/breaks/plans", ListUserBreakPlansView.as_view(), name="list-break-plans"),
    path("api/breaks/plans/<uuid:planId>", UpdateBreakPlanView.as_view(), name="update-break-plan"),
    path("api/breaks/plan/<uuid:planId>", DeleteBreakPlanView.as_view(), name="delete-break-plan"),


    path("api/user/settings", UserSettingsView.as_view(), name="user_settings"),

]





    
