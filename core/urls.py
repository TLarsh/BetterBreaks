from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    RequestOTPView,
    VerifyOTPView,
    ResetPasswordView,
    ChangeEmailView,
    ChangePasswordView,
    GoogleLoginView, FacebookLoginView, TwitterLoginView,
    DateListView,
    SendMessageView,
    SpecialDateListCreateView,
    SpecialDateDetailView,
    BlackoutDatesView,
    ProfileView,
    UpdateProfileView,
    # UpdateSettingsView,
    GetSettingsView,
    # LogActionView,
    # UpdateWellbeingView,
    # GetOnboardingDataView,
    # UpdateOnboardingDataView,
    # FetchPublicHolidaysView,
    # ListPublicHolidaysView,
    # OptimizationScoreView,
    # GamificationDataView,
    # SuggestedDatesView,
    # WellbeingQuestionView,
    AddDateView,
    DeleteDateView,
    AddBlackoutDateView,
    DeleteBlackoutDateView,
    CreateBreakPlanView,
    UpcomingBreaksView,
    ListUserBreakPlansView,
    UpdateBreakPlanView,
    DeleteBreakPlanView,
    UserSettingsView,
    NotificationPreferenceView,
    ScheduleView,
    FirstLoginSetupView,
    FirstLoginSetupUpdateView,
    FirstLoginSetupDataView,
    MoodCheckInView,
    MoodHistoryView,
    WeatherForecastView,
    EventListView,
    InitiatePaymentView,
    VerifyPaymentView,
    # New APIView classes
    BreakLogListCreateView,
    BreakSuggestionListCreateView,
    BreakPlanActionView,
    BreakLogDetailView,
    ScoreSummaryView,
    StreakListCreateView,
    StreakDetailView,
    BadgeListCreateView,
    BadgeDetailView,
    BadgeEligibilityView,
    OptimizationListCreateView,
    OptimizationDetailView,
    OptimizationCalculateView,


    HolidayView, 
    # HolidayDetailView, 
    UpcomingHolidaysView,
    
)
from .social import AppleLoginView, TwitterLoginView, GoogleLoginView
# from .payments import InitializePaymentView, VerifyPaymentView, PaystackWebhookView


from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
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
from .swagger_api_fe import (
    schedule_get_schema, 
    schedule_post_schema, 
    google_login_schema, 
    facebook_login_schema, 
    twitter_login_schema,
    mood_checkin_schema,
    mood_history_schema,
)


# Removed router as we're now using APIViews instead of ViewSets

urlpatterns = [
    # Break logs endpoints
    path('api/breaks/logs/', BreakLogListCreateView.as_view(), name='break-logs-list'),
    path('api/breaks/logs/<int:pk>/', BreakLogDetailView.as_view(), name='break-logs-detail'),
    
    # Score endpoints
    path('api/score/summary/', ScoreSummaryView.as_view(), name='score-summary'),
    
    # Streak endpoints
    path('api/streaks/', StreakListCreateView.as_view(), name='streaks-list'),
    path('api/streaks/<int:pk>/', StreakDetailView.as_view(), name='streaks-detail'),
    
    # Badge endpoints
    path('api/badges/', BadgeListCreateView.as_view(), name='badges-list'),
    path('api/badges/<int:pk>/', BadgeDetailView.as_view(), name='badges-detail'),
    # path('api/badges/check-eligibility/', BadgeEligibilityView.as_view(), name='badges-check-eligibility'),
    
    # Optimization endpoints
    path('api/optimization/', OptimizationListCreateView.as_view(), name='optimization-list'),
    path('api/optimization/<int:pk>/', OptimizationDetailView.as_view(), name='optimization-detail'),
    # path('api/optimization/calculate/', OptimizationCalculateView.as_view(), name='optimization-calculate'),
    
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),  # Ensure 'register' matches test
    path('api/auth/login/', LoginView.as_view(), name='login'),          # Ensure 'login' matches test
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),      # Ensure 'logout' matches test
    path('api/auth/request-reset/', RequestOTPView.as_view()),
    path('api/auth/verify-otp/', VerifyOTPView.as_view()),
    path('api/auth/reset-password/', ResetPasswordView.as_view()),
    path("api/auth/change-email/", ChangeEmailView.as_view(), name="change-email"),
    path("api/auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    
    # Holidays (APIViews replacing ViewSet)
     path('api/holidays/', HolidayView.as_view(), name='holiday-list'),
    #  path('api/holidays/<int:pk>/', HolidayDetailView.as_view(), name='holiday-detail'),
     path('api/holidays/upcoming/', UpcomingHolidaysView.as_view(), name='upcoming-holidays'),


    # path("api/auth/google/", GoogleLoginView.as_view(), name="google-login"),
    # path("api/auth/facebook/", FacebookLoginView.as_view(), name="facebook-login"),
    # path("api/auth/twitter/", TwitterLoginView.as_view(), name="twitter-login"),

    path("api/auth/google/", GoogleLoginView.as_view(), name="google-login"),
    path("api/auth/twitter/", TwitterLoginView.as_view(), name="twitter-login"),
    # path("api/auth/apple/", AppleLoginView.as_view(), name="apple-login"),

    path("api/message/send/", SendMessageView.as_view(), name="send-message"),

    # path('api/blackout-dates/', BlackoutDatesView.as_view(), name='blackout_dates'),
    path('api/profile/get/', ProfileView.as_view(), name='profile'),
    # path('api/update-wellbeing/', UpdateWellbeingView.as_view(), name='update_wellbeing'),
    # path('api/log-action/', LogActionView.as_view(), name='log_action'),
    path('api/profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    # path('api/update-settings/', UpdateSettingsView.as_view(), name='update_settings'),
    path('api/settings/', GetSettingsView.as_view(), name='get_settings'),
    # path('api/onboarding/get/', GetOnboardingDataView.as_view(), name='get_onboarding_data'),
    # path('api/onboarding/update/', UpdateOnboardingDataView.as_view(), name='update_onboarding_data'),
    # path("api/fetch-public-holidays/", FetchPublicHolidaysView.as_view(), name="fetch-public-holidays"),
    # path("api/list-public-holidays/", ListPublicHolidaysView.as_view(), name="list-public-holidays"),
    # path("api/optimization-score/", OptimizationScoreView.as_view(), name="optimization-score"),
    # path("api/gamification-data/", GamificationDataView.as_view(), name="gamification-data"),
    # path("api/suggested-dates/", SuggestedDatesView.as_view(), name="suggested-dates"),
    # path('api/dates/', DateListView.as_view(), name='dates'),       # Ensure 'dates' matches test
    # path("api/dates/add/", AddDateView.as_view(), name="add-date"),

    path("api/dates/special-dates/", SpecialDateListCreateView.as_view(), name="special-dates-list-create"),
    path("api/dates/special-dates/<uuid:pk>/", SpecialDateDetailView.as_view(), name="special-dates-detail"),
    path("api/dates/blackout-dates-add/", AddBlackoutDateView.as_view(),name="add-blackout-date"),
    path("api/dates/blackout-dates/", BlackoutDatesView.as_view(),name="blackout-dates"),
    path("api/dates/blackout-date-delete/<uuid:blackout_uuid>/", DeleteBlackoutDateView.as_view(),name="delete-blackout-date"),
    



    path("api/breaks/plan", CreateBreakPlanView.as_view(), name="create-break-plan"),
    path("api/breaks/upcoming", UpcomingBreaksView.as_view(), name="create-break-plan"),
    path("api/breaks/plans", ListUserBreakPlansView.as_view(), name="list-break-plans"),
    # path("api/breaks/plans/<uuid:planId>", UpdateBreakPlanView.as_view(), name="update-break-plan"),
    path("api/breaks/plan/<uuid:planId>", DeleteBreakPlanView.as_view(), name="delete-break-plan"),
    path("api/breaks/plan/action/<uuid:pk>/", BreakPlanActionView.as_view(), name="break-plan-action"),
    path("api/breaks/suggest", BreakSuggestionListCreateView.as_view(), name="list-create-break-suggestions"),
    # path("api/breaks/suggest/<uuid:pk>", BreakSuggestionDetailView.as_view(), name="break-suggestion-detail"),


    path("api/user/settings", UserSettingsView.as_view(), name="user_settings"),
    path('api/user/notification-preferences', NotificationPreferenceView.as_view()),
    path("api/schedule", ScheduleView.as_view(), name="schedule"),
    path("api/onboarding/set/", FirstLoginSetupView.as_view(), name="onboarding"),
    path("api/onboarding/setup-update/", FirstLoginSetupUpdateView.as_view(), name="first-login-setup-update"),
    path("api/onboarding/setup-data/", FirstLoginSetupDataView.as_view(), name="first-login-setup-data"),

    path("api/weather/forecast/", WeatherForecastView.as_view(), name="weather-forecast"),

    path(
        "api/moods/checkin/",
        MoodCheckInView.as_view(),
        name='mood-checkin'
    ),
    path(
        "api/moods/history/",
        MoodHistoryView.as_view(),
        name='mood-history'
    ),

    # path("events/", EventListView.as_view(), name="list_events"),
    
    # --- Payments ---
    path("api/bookings/<int:booking_id>/payments/initiate/", InitiatePaymentView.as_view(), name="initiate-payment"),
    path("api/bookings/<int:booking_id>/payments/verify/", VerifyPaymentView.as_view(), name="verify-payment"),
    # path("api/payments/webhook/", PaystackWebhookView.as_view(), name="paystack-webhook"),




    # path('api/', include(router.urls)),


]





    
