from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    RequestOTPView,
    VerifyOTPView,
    ResetPasswordView,
    GoogleLoginView, FacebookLoginView, TwitterLoginView,
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
    NotificationPreferenceView,
    ScheduleView,
    FirstLoginSetupView,
    MoodCheckInView,
    MoodHistoryView,
    WeatherForecastView,
    EventListView,
    InitiatePaymentView,
    VerifyPaymentView,
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


urlpatterns = [
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),  # Ensure 'register' matches test
    path('api/auth/login/', LoginView.as_view(), name='login'),          # Ensure 'login' matches test
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),      # Ensure 'logout' matches test
    path('api/auth/request-reset/', RequestOTPView.as_view()),
    path('api/auth/verify-otp/', VerifyOTPView.as_view()),
    path('api/auth/reset-password/', ResetPasswordView.as_view()),


    # path("api/auth/google/", GoogleLoginView.as_view(), name="google-login"),
    # path("api/auth/facebook/", FacebookLoginView.as_view(), name="facebook-login"),
    # path("api/auth/twitter/", TwitterLoginView.as_view(), name="twitter-login"),

    path("api/auth/google/", GoogleLoginView.as_view(), name="google-login"),
    path("api/auth/twitter/", TwitterLoginView.as_view(), name="twitter-login"),
    # path("api/auth/apple/", AppleLoginView.as_view(), name="apple-login"),

    path('api/dates/', DateListView.as_view(), name='dates'),       # Ensure 'dates' matches test
    path('api/blackout-dates/', BlackoutDatesView.as_view(), name='blackout_dates'),
    path('api/profile/get/', ProfileView.as_view(), name='profile'),
    path('api/update-wellbeing/', UpdateWellbeingView.as_view(), name='update_wellbeing'),
    path('api/log-action/', LogActionView.as_view(), name='log_action'),
    path('api/profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    # path('api/update-settings/', UpdateSettingsView.as_view(), name='update_settings'),
    # path('api/settings/', GetSettingsView.as_view(), name='get_settings'),
    path('api/onboarding/get/', GetOnboardingDataView.as_view(), name='get_onboarding_data'),
    path('api/onboarding/update/', UpdateOnboardingDataView.as_view(), name='update_onboarding_data'),
    path("api/fetch-public-holidays/", FetchPublicHolidaysView.as_view(), name="fetch-public-holidays"),
    path("api/list-public-holidays/", ListPublicHolidaysView.as_view(), name="list-public-holidays"),
    path("api/optimization-score/", OptimizationScoreView.as_view(), name="optimization-score"),
    path("api/gamification-data/", GamificationDataView.as_view(), name="gamification-data"),
    path("api/suggested-dates/", SuggestedDatesView.as_view(), name="suggested-dates"),
    path("api/dates/add/", AddDateView.as_view(), name="add-date"),



    path("api/breaks/plan", CreateBreakPlanView.as_view(), name="create-break-plan"),
    path("api/breaks/plans", ListUserBreakPlansView.as_view(), name="list-break-plans"),
    path("api/breaks/plans/<uuid:planId>", UpdateBreakPlanView.as_view(), name="update-break-plan"),
    path("api/breaks/plan/<uuid:planId>", DeleteBreakPlanView.as_view(), name="delete-break-plan"),


    path("api/user/settings", UserSettingsView.as_view(), name="user_settings"),
    path('api/user/notification-preferences', NotificationPreferenceView.as_view()),
    path("api/schedule", ScheduleView.as_view(), name="schedule"),
    path("api/onboarding/set/", FirstLoginSetupView.as_view(), name="onboarding"),

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


]





    
