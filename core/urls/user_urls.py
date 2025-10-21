from django.urls import path
from ..views.user_views import (
    RegisterView,
    LoginView,
    LogoutView,
    RequestOTPView, VerifyOTPView,
    ResetPasswordView,
    ChangeEmailView,
    ChangePasswordView,
    ProfileView,
    UpdateProfileView,
    GoogleLoginView, FacebookLoginView, TwitterLoginView,
)


urlpatterns = [
    # path("api/user/settings", UserSettingsView.as_view(), name="user_settings"),
    # path('api/user/notification-preferences', NotificationPreferenceView.as_view()),
    path('api/profile/get/', ProfileView.as_view(), name='profile'),
    path('api/profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('api/auth/register/', RegisterView.as_view(), name='register'),  # Ensure 'register' matches test
    path('api/auth/login/', LoginView.as_view(), name='login'),          # Ensure 'login' matches test
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),      # Ensure 'logout' matches test
    path('api/auth/request-reset/', RequestOTPView.as_view()),
    path('api/auth/verify-otp/', VerifyOTPView.as_view()),
    path('api/auth/reset-password/', ResetPasswordView.as_view()),
    path("api/auth/change-email/", ChangeEmailView.as_view(), name="change-email"),
    path("api/auth/change-password/", ChangePasswordView.as_view(), name="change-password"),



    path("api/auth/google/", GoogleLoginView.as_view(), name="google-login"),
    path("api/auth/facebook/", FacebookLoginView.as_view(), name="facebook-login"),
    path("api/auth/twitter/", TwitterLoginView.as_view(), name="twitter-login"),

    # path("api/auth/google/", GoogleLoginView.as_view(), name="google-login"),
    # path("api/auth/twitter/", TwitterLoginView.as_view(), name="twitter-login"),
    # path("api/auth/apple/", AppleLoginView.as_view(), name="apple-login"),
]