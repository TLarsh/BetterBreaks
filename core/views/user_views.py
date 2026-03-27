import token
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.contrib.auth import get_user_model
from django.conf import settings
from .social_base_login_views import BaseSocialLoginView
from drf_yasg.utils import swagger_auto_schema

from ..models.leave_balance_models import LeaveBalance
from ..models.preference_models import BreakPreferences
from ..models.break_models import BreakPlan

from dateutil.parser import isoparse as date_parser
from django.contrib.auth.password_validation import validate_password
from core.tasks.holiday_tasks import sync_user_holidays
from ..utils.contry_code_resolution import timezone_to_country_code, update_user_location
from django.utils import timezone


# =======SOCIAL ALLAUTH ACCOUNT PROVIDERS=====
# from drf_yasg.utils import swagger_auto_schema
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth.client import OAuthClient
# =============================================

from core.docs.user_docs import (
    google_login_schema,
    facebook_login_schema,
    twitter_login_schema,
    email_login_schema,
    apple_login_schema,
)
from core.serializers.user_serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    RequestOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    UserSerializer
)
from core.models.user_models import LastLogin
from core.utils.responses import success_response, error_response
from ..utils.user_utils import validate_and_create_user
import logging
import traceback
import requests

from core.services.notification_service import NotificationService
from core.helpers.mobile_google_login import verify_google_id_token, handle_mobile_google_login
from core.helpers.mobile_apple_login import verify_apple_id_token, handle_apple_login
from dj_rest_auth.registration.views import SocialLoginView
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


User = get_user_model()


class RegisterView(APIView):
    """Handle user registration with password validation."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RegisterSerializer,
        operation_summary="Register a new user",
        operation_description="Registers a new user with email, optional full name, and password confirmation."
    )
    def post(self, request):
        try:
            user = validate_and_create_user(request.data)
            # update_user_location(user, timezone=timezone, coords=coords)

            NotificationService.notify(
            user=user,
            event="welcome",
            title="Welcome to BetterBreaks! 🎉",
            message=(
                "We're excited to have you on board. "
                "Start by setting up your leave balance and let us help you plan smarter breaks."
            ),
            metadata={}
        )

            return success_response(
                message="Registration successful",
                data={
                    "email": user.email,
                    "full_name": user.full_name
                },
                status_code=status.HTTP_201_CREATED
            )

        except DRFValidationError as ve:
            return error_response(
                message="Registration failed",
                errors=ve.detail if hasattr(ve, "detail") else str(ve),
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
        except ValueError as ve:
            return error_response(
                message="Registration failed",
                errors={"detail": str(ve)},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return error_response(
                message="An unexpected error occurred during registration",
                errors={"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )

class LoginView(APIView):
    permission_classes = [AllowAny]

    # @swagger_auto_schema(request_body=LoginSerializer)
    @email_login_schema
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            tokens = user.tokens()

            LastLogin.objects.create(
                user=user,
                client=user,
                ip_address=request.META.get("REMOTE_ADDR", ""),
                token=tokens["access"],
                token_valid=True,
            )

            onboarding_completed = bool(
            LeaveBalance.objects.filter(user=user).exists()
            and BreakPreferences.objects.filter(user=user).exists()
            and BreakPlan.objects.filter(user=user).exists()
        )

            return success_response(
                message="Login successful",
                data={
                    "email": user.email,
                    "full_name": user.full_name,
                    "access": tokens["access"],
                    "refresh": tokens["refresh"],
                    "onboarding_completed": onboarding_completed,
                }
            )

        return error_response(
            message="Incorrect email or password",
            errors=serializer.errors
        )





class GoogleLoginView(SocialLoginView):
    permission_classes = [AllowAny]
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    @google_login_schema
    def post(self, request, *args, **kwargs):
        try:
            id_token_str = request.data.get("id_token")
            code = request.data.get("code")
            access_token = request.data.get("access_token")
            timezone = request.data.get("timezone")
            coords = request.data.get("coordinates")

            # =========================
            #  MOBILE FLOW (ID TOKEN)
            # =========================
            if id_token_str:
                # idinfo = verify_google_id_token(id_token_str)
                idinfo = verify_google_id_token(id_token_str)

                if not idinfo:
                    return error_response(
                        message="Invalid Google ID token",
                        errors={"id_token": "Verification failed"},
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                user = handle_mobile_google_login(idinfo)
                update_user_location(user, timezone=timezone, coords=coords)

                if not user:
                    return error_response(
                        message="User creation failed",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

            # =========================
            # WEB FLOW (CODE / ACCESS TOKEN)
            # =========================
            elif code or access_token:
                self.callback_url = settings.GOOGLE_CALLBACK_URL

                response = super().post(request, *args, **kwargs)

                if response.status_code != 200:
                    return error_response(
                        message="Google web login failed",
                        errors=response.data
                    )

                user = self.serializer.validated_data["user"]

            else:
                return error_response(
                    message="Provide id_token, code, or access_token",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # =========================
            # ISSUE JWT TOKENS
            # =========================
            refresh = RefreshToken.for_user(user)

            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            # =========================
            # LOG LOGIN
            # =========================
            LastLogin.objects.create(
                user=user,
                client=user,
                ip_address=request.META.get("REMOTE_ADDR", ""),
                token=tokens["access"],
                token_valid=True,
            )

            onboarding_completed = bool(
            LeaveBalance.objects.filter(user=user).exists()
            and BreakPreferences.objects.filter(user=user).exists()
            and BreakPlan.objects.filter(user=user).exists()
            )

            return success_response(
                message="Google login successful",
                data={
                    "email": user.email,
                    "full_name": user.full_name,
                    "access": tokens["access"],
                    "refresh": tokens["refresh"],
                    "onboarding_completed": onboarding_completed,
                    "provider": "google"
                }
            )

        except Exception as e:
            traceback.print_exc()

            return error_response(
                message="An unexpected error occurred.",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        

class AppleLoginView(SocialLoginView):
    permission_classes = [AllowAny]
    adapter_class = AppleOAuth2Adapter
    client_class = OAuth2Client

    @apple_login_schema
    def post(self, request, *args, **kwargs):
        try:
            id_token_str = request.data.get("id_token")
            code = request.data.get("code")
            timezone = request.data.get("timezone")
            coords = request.data.get("coordinates")

            first_name = request.data.get("first_name")
            last_name = request.data.get("last_name")

            # =========================
            # MOBILE FLOW (ID TOKEN)
            # =========================
            if id_token_str:
                payload = verify_apple_id_token(id_token_str)

                if not payload:
                    return error_response(
                        message="Invalid Apple ID token",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                user = handle_apple_login(
                    payload,
                    first_name=first_name,
                    last_name=last_name
                )

                update_user_location(user, timezone=timezone, coords=coords)

                if not user:
                    return error_response(
                        message="User creation failed",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

            # =========================
            # WEB FLOW (CODE)
            # =========================
            elif code:
                self.callback_url = settings.APPLE_CALLBACK_URL

                response = super().post(request, *args, **kwargs)

                if response.status_code != 200:
                    return error_response(
                        message="Apple web login failed",
                        errors=response.data
                    )

                user = self.serializer.validated_data["user"]

            else:
                return error_response(
                    message="Provide id_token or code",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # =========================
            # ISSUE TOKENS
            # =========================
            refresh = RefreshToken.for_user(user)

            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            # =========================
            # LOG LOGIN
            # =========================
            LastLogin.objects.create(
                user=user,
                ip_address=request.META.get("REMOTE_ADDR", ""),
                token=tokens["access"],
                token_valid=True,
            )

            return success_response(
                message="Apple login successful",
                data={
                    "email": user.email,
                    "full_name": user.full_name,
                    "access": tokens["access"],
                    "refresh": tokens["refresh"],
                    "provider": "apple"
                }
            )

        except Exception as e:
            traceback.print_exc()

            return error_response(
                message="An unexpected error occurred.",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FacebookLoginView(BaseSocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    client_class = OAuth2Client
    @facebook_login_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class TwitterLoginView(BaseSocialLoginView):
    adapter_class = TwitterOAuthAdapter
    client_class = OAuthClient  # OAuth 1.0a for Twitter
    @twitter_login_schema
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)       

class LogoutView(APIView):
    """Handle user logout by blacklisting the refresh token."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LogoutSerializer)
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return error_response(
                message="Refresh token is required",
                errors={"refresh": ["Refresh token is required"]},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            token_obj = RefreshToken(refresh_token)

            jti = token_obj["jti"]
            LastLogin.objects.filter(token=jti).update(token_valid=False)

            token_obj.blacklist()

            return success_response(
                message="Logout successful",
                data=None,
                status_code=status.HTTP_200_OK
            )

        except TokenError as e:
            return error_response(
                message="Invalid token",
                errors={"refresh": [str(e)]},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return error_response(
                message="Server error",
                errors={"non_field_errors": ["An unexpected error occurred"]},
                status_code=status.HTTP_400_BAD_REQUEST
            )        


class RequestOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=RequestOTPSerializer,
        operation_summary="Request OTP for password reset",
        operation_description="Generates a 6-digit OTP and sends it to the provided email address."
    )
    def post(self, request):
        try:
            serializer = RequestOTPSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return success_response(
                    message="OTP sent successfully to your email.",
                    data=None,
                    status_code=status.HTTP_200_OK
                )

            return error_response(
                message="Failed to send OTP",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return error_response(
                message="An unexpected error occurred while sending OTP",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=VerifyOTPSerializer)
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="OTP verified successfully.",
                data=None,
                status_code=status.HTTP_200_OK
            )
        return error_response(
            message="OTP verification failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Password reset successful.",
                data=None,
                status_code=status.HTTP_200_OK
            )
        return error_response(
            message="Password reset failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

########### CHANGE EMAIL AND PASSWORD VIEW ###################

class ChangeEmailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ChangeEmailSerializer)
    def post(self, request):
        serializer = ChangeEmailSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Email updated successfully.",
                data={"email": request.user.email},
                status_code=status.HTTP_200_OK
            )
        return error_response(
            message="Email update failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=ChangePasswordSerializer)
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Password updated successfully.",
                data=None,
                status_code=status.HTTP_200_OK
            )
        return error_response(
            message="Password update failed.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
    



############### USER PROFILE VIEWS #####################
######################################################## 
class ProfileView(APIView):
    """Retrieve user profile details."""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return error_response(
                message="Unauthorized",
                errors={"detail": "Authentication credentials were not provided."},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        serializer = UserSerializer(request.user)
        return success_response(
            message="Profile retrieved",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
    



class UpdateProfileView(APIView):
    """Update user profile details."""

    @swagger_auto_schema(request_body=UserSerializer)
    def post(self, request):
        if not request.user.is_authenticated:
            return error_response(
                message="Unauthorized",
                errors={"auth": "You must be logged in."},
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        user = request.user
        data = request.data.copy()

        # Convert and validate birthday
        birthday_str = data.get("birthday")
        if birthday_str:
            try:
                data["birthday"] = date_parser(birthday_str)
            except Exception:
                return error_response(
                    message="Invalid date format for birthday",
                    errors={"birthday": "Use ISO format e.g. 2025-07-23T05:36:26Z"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # Validate password (if provided)
        new_password = data.get("password")
        if new_password:
            try:
                validate_password(new_password)
                user.set_password(new_password)
                user.save()
            except (ValueError, DRFValidationError) as e:
                return error_response(
                    message="Password validation failed",
                    errors={"password": str(e)},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return error_response(
                    message="Password validation failed",
                    errors={"password": str(e)},
                    status_code=status.HTTP_400_BAD_REQUEST
                )

        # --- Track if user updates country/timezone ---
        old_timezone = getattr(user, "home_location_timezone", None)
        old_coords = getattr(user, "home_location_coordinates", None)

        # Validate other fields via serializer
        serializer = UserSerializer(instance=user, data=data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()

            timezone_changed = old_timezone != getattr(updated_user, "home_location_timezone", None)
            coords_changed = old_coords != getattr(updated_user, "home_location_coordinates", None)

            if timezone_changed or coords_changed:
                calendar = getattr(updated_user, "holiday_calendar", None)
                if calendar:
                    # Infer country code from timezone
                    country_code = timezone_to_country_code(updated_user.home_location_timezone)
                    calendar.country_code = country_code
                    calendar.last_synced = timezone.now()
                    calendar.save(update_fields=["country_code", "last_synced"])

                    # Trigger Celery sync
                    try:
                        sync_user_holidays.delay(str(updated_user.id), calendar.country_code)
                    except Exception:
                        # don't fail the whole request if task scheduling fails
                        pass

            return success_response(
                message="Profile updated successfully",
                data=serializer.data,
                status_code=status.HTTP_200_OK
            )

        else:
            return error_response(
                message="Validation failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )