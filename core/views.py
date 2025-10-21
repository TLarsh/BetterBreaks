from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.utils import timezone
from django.db.models import Q, Avg
from django.utils.timezone import now
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.contrib.auth import get_user_model
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import timedelta, date, datetime, time
from dateutil import parser as date_parser
from .utils.validator_utils import validate_password
from .models import (LeaveBalance, BreakPreferences, OptimizationGoal, UserNotificationPreference, WorkingPattern, 
BreakScore, StreakScore, Badge, OptimizationScore
# GamificationData
)
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    RequestOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    ChangeEmailSerializer,
    ChangePasswordSerializer,
    UserSerializer,
    ContactMessageSerializer,
    DateEntrySerializer,
    BlackoutDateSerializer,
    BlackOutDateSerializer,
    SpecialDateSerializer,
    # UpdateSettingsSerializer,
    ActionLogSerializer,
    PublicHolidaySerializer,
    # OnboardingDataSerializer,
    # WellbeingScoreSerializer,
    # WellbeingQuestionSerializer,
    # GamificationDataSerializer,
    # _____BreakSerializer_______
    BreakPlanSerializer,
    UpcomingBreakPlanSerializer,
    BreakPlanListSerializer,
    BreakPlanActionSerializer,
    BreakPlanUpdateSerializer,
    LeaveBalanceSerializer, BreakPreferencesSerializer, BreakPlanSerializer,
    # Gamification serializers
    BreakScoreSerializer, StreakScoreSerializer, BadgeSerializer, OptimizationScoreSerializer,
    #______firstLoginSetupSerializer____
    FirstLoginSetupSerializer,
    FirstLoginSetupDataSerializer,
    # Gamification serializers
    BreakScoreSerializer,
    BreakSuggestionSerializer,
    StreakScoreSerializer,
    BadgeSerializer,
    OptimizationScoreSerializer,
    # _____settingsSerializer___
    UserSettingsSerializer,
    # _____notificationSerializer___
    NotificationPreferenceSerializer,
    # _____Schedule___
    WorkingPatternSerializer,
    OptimizationGoalSerializer,
    # _____Mood___
    MoodCheckInSerializer, MoodHistorySerializer,
    # _____Events___
    EventSerializer, BookingSerializer,
    #_____Weather___
    WeatherForecastDaySerializer,

)
from .models import (
    LastLogin,
    UserSettings,
    DateEntry,
    ActionData,
    Client,
    LeaveBalance, BreakSuggestion, BreakPreferences, OptimizationGoal, UserNotificationPreference, WorkingPattern, 
    BlackoutDate,
    SpecialDate,
    # GamificationData,
    PublicHoliday,
    PublicHolidayCalendar,
    # OnboardingData,
    # GamificationData,
    # WellbeingScore,
    # WellbeingQuestion,
    
    BreakPlan,
    Mood,

    Event, Booking

)

# from .swagger_api_fe import (
#     schedule_get_schema, 
#     schedule_post_schema, 
#     google_login_schema, 
#     facebook_login_schema, 
#     twitter_login_schema,
#     mood_checkin_schema,
#     mood_history_schema,
#     first_login_setup_docs,
#     event_list_docs,
#     book_event_docs,
#     weather_forecast_schema,
#     initiate_payment_docs,
#     verify_payment_docs,
#     holiday_detail_get,
#     # holiday_detail_post,
#     holiday_detail_put,
#     holiday_detail_delete,
#     upcoming_holidays_get,
#     break_plan_action,
#     break_log_list,
#     break_log_create,
#     break_log_retrieve,
#     break_log_update,
#     break_log_delete,
#     optimization_list,
#     optimization_create,
#     optimization_retrieve,
#     optimization_update,
#     optimization_delete,
#     optimization_calculate,
#     score_summary,
#     streak_list,
#     streak_create,
#     streak_retrieve,
#     streak_update,
#     streak_delete,
#     badge_list,
#     badge_create,
#     badge_retrieve,
#     badge_update,
#     badge_delete,
#     badge_eligibility,

# )
# from.utils.user_utils import validate_and_create_user
# from .utils import (
#     create_calendar_event, 
#     fetch_public_holidays,
#     # calculate_smart_planning_score,
#     # award_badges,
#     # generate_holiday_suggestions,
#     # fetch_weather_data,
#     adjust_score_based_on_weather, 
#     success_response, error_response, 
#     fetch_6day_weather_forecast_openweathermap,
# )

# from .utils.payment_gateways import PaystackGateway

# from drf_yasg.utils import swagger_auto_schema
# from drf_yasg import openapi
# import logging
# import traceback
# import random
# import uuid



# # =======SOCIAL ALLAUTH ACCOUNT PROVIDERS=====
# # from drf_yasg.utils import swagger_auto_schema
# from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
# from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
# from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
# from allauth.socialaccount.providers.oauth2.client import OAuth2Client
# from allauth.socialaccount.providers.oauth.client import OAuthClient
# # =============================================

# from .views.social_base_login_views import BaseSocialLoginView

# logger = logging.getLogger(__name__)


# User = get_user_model()  # Ensure your custom user model is properly configured


# class RegisterView(APIView):
#     """Handle user registration with password validation."""
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         request_body=RegisterSerializer,
#         operation_summary="Register a new user",
#         operation_description="Registers a new user with email, optional full name, and password confirmation."
#     )
#     def post(self, request):
#         try:
#             user = validate_and_create_user(request.data)

#             return success_response(
#                 message="Registration successful",
#                 data={
#                     "email": user.email,
#                     "full_name": user.full_name
#                 },
#                 status_code=status.HTTP_201_CREATED
#             )

#         except DRFValidationError as ve:
#             return error_response(
#                 message="Registration failed",
#                 errors=ve.detail if hasattr(ve, "detail") else str(ve),
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )
            
#         except ValueError as ve:
#             return error_response(
#                 message="Registration failed",
#                 errors={"detail": str(ve)},
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

#         except Exception as e:
#             return error_response(
#                 message="An unexpected error occurred during registration",
#                 errors={"detail": str(e)},
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

# class LoginView(APIView):
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(request_body=LoginSerializer)
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.validated_data["user"]

#             tokens = user.tokens()

#             LastLogin.objects.create(
#                 user=user,
#                 client=user,
#                 ip_address=request.META.get("REMOTE_ADDR", ""),
#                 token=tokens["access"],
#                 token_valid=True,
#             )

#             return success_response(
#                 message="Login successful",
#                 data={
#                     "refresh": tokens["refresh"],
#                     "access": tokens["access"],
#                     "email": user.email,
#                     "full_name": user.full_name,
#                 }
#             )

#         return error_response(
#             message="Login failed",
#             errors=serializer.errors
#         )


# class GoogleLoginView(BaseSocialLoginView):
#     adapter_class = GoogleOAuth2Adapter
#     client_class = OAuth2Client
#     @google_login_schema
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)


# class FacebookLoginView(BaseSocialLoginView):
#     adapter_class = FacebookOAuth2Adapter
#     client_class = OAuth2Client
#     @facebook_login_schema
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)


# class TwitterLoginView(BaseSocialLoginView):
#     adapter_class = TwitterOAuthAdapter
#     client_class = OAuthClient  # OAuth 1.0a for Twitter
#     @twitter_login_schema
#     def post(self, request, *args, **kwargs):
#         return super().post(request, *args, **kwargs)       

# class LogoutView(APIView):
#     """Handle user logout by blacklisting the refresh token."""
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(request_body=LogoutSerializer)
#     def post(self, request):
#         refresh_token = request.data.get("refresh")
#         if not refresh_token:
#             return error_response(
#                 message="Refresh token is required",
#                 errors={"refresh": ["Refresh token is required"]},
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             token_obj = RefreshToken(refresh_token)

#             jti = token_obj["jti"]
#             LastLogin.objects.filter(token=jti).update(token_valid=False)

#             token_obj.blacklist()

#             return success_response(
#                 message="Logout successful",
#                 data=None,
#                 status_code=status.HTTP_200_OK
#             )

#         except TokenError as e:
#             return error_response(
#                 message="Invalid token",
#                 errors={"refresh": [str(e)]},
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

#         except Exception:
#             return error_response(
#                 message="Server error",
#                 errors={"non_field_errors": ["An unexpected error occurred"]},
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )        


# class RequestOTPView(APIView):
#     authentication_classes = []
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(
#         request_body=RequestOTPSerializer,
#         operation_summary="Request OTP for password reset",
#         operation_description="Generates a 6-digit OTP and sends it to the provided email address."
#     )
#     def post(self, request):
#         try:
#             serializer = RequestOTPSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return success_response(
#                     message="OTP sent successfully to your email.",
#                     data=None,
#                     status_code=status.HTTP_200_OK
#                 )

#             return error_response(
#                 message="Failed to send OTP",
#                 errors=serializer.errors,
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

#         except Exception as e:
#             return error_response(
#                 message="An unexpected error occurred while sending OTP",
#                 errors={"detail": str(e)},
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# class VerifyOTPView(APIView):
#     authentication_classes = []
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(request_body=VerifyOTPSerializer)
#     def post(self, request):
#         serializer = VerifyOTPSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return success_response(
#                 message="OTP verified successfully.",
#                 data=None,
#                 status_code=status.HTTP_200_OK
#             )
#         return error_response(
#             message="OTP verification failed",
#             errors=serializer.errors,
#             status_code=status.HTTP_400_BAD_REQUEST
#         )


# class ResetPasswordView(APIView):
#     authentication_classes = []
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(request_body=ResetPasswordSerializer)
#     def post(self, request):
#         serializer = ResetPasswordSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return success_response(
#                 message="Password reset successful.",
#                 data=None,
#                 status_code=status.HTTP_200_OK
#             )
#         return error_response(
#             message="Password reset failed",
#             errors=serializer.errors,
#             status_code=status.HTTP_400_BAD_REQUEST
#         )

# ########### CHANGE EMAIL AND PASSWORD VIEW ###################

# class ChangeEmailView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(request_body=ChangeEmailSerializer)
#     def post(self, request):
#         serializer = ChangeEmailSerializer(data=request.data, context={"request": request})
#         if serializer.is_valid():
#             serializer.save()
#             return success_response(
#                 message="Email updated successfully.",
#                 data={"email": request.user.email},
#                 status_code=status.HTTP_200_OK
#             )
#         return error_response(
#             message="Email update failed.",
#             errors=serializer.errors,
#             status_code=status.HTTP_400_BAD_REQUEST
#         )


# class ChangePasswordView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(request_body=ChangePasswordSerializer)
#     def post(self, request):
#         serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
#         if serializer.is_valid():
#             serializer.save()
#             return success_response(
#                 message="Password updated successfully.",
#                 data=None,
#                 status_code=status.HTTP_200_OK
#             )
#         return error_response(
#             message="Password update failed.",
#             errors=serializer.errors,
#             status_code=status.HTTP_400_BAD_REQUEST
#         )

##### CONTACT US ##############################################

# class SendMessageView(APIView):
#     """Send us a message API"""
#     authentication_classes = []
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(request_body=ContactMessageSerializer)
#     def post(self, request):
#         serializer = ContactMessageSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return success_response(
#                 message="Your message has been received. We’ll get back to you soon.",
#                 data=None,
#                 status_code=status.HTTP_201_CREATED
#             )
#         return error_response(
#             message="Failed to send message.",
#             errors=serializer.errors,
#             status_code=status.HTTP_400_BAD_REQUEST
#         )

# ######## DATE LIST ################

# class DateListView(APIView):
#     """Retrieve authenticated user's dates."""
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         dates = DateEntry.objects.filter(user=request.user)
#         serializer = DateEntrySerializer(dates, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)



# class BookEventView(APIView):
#     @swagger_auto_schema(request_body=DateEntrySerializer)
#     def post(self, request, date_entry_id):
#         try:
#             date_entry = DateEntry.objects.get(id=date_entry_id, user=request.user)
#             create_calendar_event(request.user, date_entry)
#             return Response({"success": True}, status=status.HTTP_200_OK)
#         except DateEntry.DoesNotExist:
#             return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
        
# class LogoutView(APIView):
#     """Handle user logout by blacklisting the refresh token."""
#     permission_classes = [AllowAny]

#     @swagger_auto_schema(request_body=LogoutSerializer)
#     def post(self, request):
#         refresh_token = request.data.get("refresh")
#         if not refresh_token:
#             return Response(
#                 {"errors": ["Refresh token is required"]},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
        
#             token_obj = RefreshToken(refresh_token)

            
#             jti = token_obj["jti"]
#             LastLogin.objects.filter(token=jti).update(token_valid=False)

            
#             token_obj.blacklist()

#             return Response(status=status.HTTP_200_OK)

#         except TokenError as e:
#             return Response(
#                 {"errors": [str(e)]},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         except Exception as e:
#             return Response(
#                 {"errors": ["Server error"]},
#                 status=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )
        
# class FetchPublicHolidaysView(APIView):
#     def get(self, request):
#         user = request.user
#         if not user.home_location_timezone:
#             return Response({"error": "User location not set"}, status=status.HTTP_400_BAD_REQUEST)

#         country_code = user.home_location_timezone.split("/")[0]  # Extract country code
#         year = timezone.now().year
#         holidays_data = fetch_public_holidays(country_code, year)

#         for holiday in holidays_data:
#             PublicHoliday.objects.update_or_create(
#                 user=user,
#                 date=holiday["date"],
#                 defaults={"name": holiday["name"], "country_code": country_code}
#             )

#         return Response({"success": True}, status=status.HTTP_200_OK)
    

# class ListPublicHolidaysView(APIView):
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

#         holidays = PublicHoliday.objects.filter(user=request.user)
#         serializer = PublicHolidaySerializer(holidays, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)




# ############### USER PROFILE VIEWS #####################
# ######################################################## 
# class ProfileView(APIView):
#     """Retrieve user profile details."""
    
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# ############### SPECIAL DATE VIEWS #####################
# ######################################################## 
# class SpecialDateListCreateView(APIView):
#     """
#     List all special dates or create a new one.
#     """

#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_summary="List Special Dates",
#         responses={200: SpecialDateSerializer(many=True)}
#     )
#     def get(self, request, *args, **kwargs):
#         special_dates = SpecialDate.objects.filter(user=request.user)
#         serializer = SpecialDateSerializer(special_dates, many=True)
#         return success_response(
#             message="Special dates retrieved successfully",
#             data=serializer.data,
#         )

#     @swagger_auto_schema(
#         operation_summary="Create Special Date",
#         request_body=SpecialDateSerializer,
#         responses={201: SpecialDateSerializer}
#     )
#     def post(self, request, *args, **kwargs):
#         serializer = SpecialDateSerializer(data=request.data)
#         if serializer.is_valid():
#             special_date = serializer.save(user=request.user)
#             return success_response(
#                 message="Special date created successfully",
#                 data=SpecialDateSerializer(special_date).data,
#                 status_code=status.HTTP_201_CREATED,
#             )
#         return error_response(
#             message="Validation error",
#             errors=serializer.errors,
#             status_code=status.HTTP_400_BAD_REQUEST,
#         )


# class SpecialDateDetailView(APIView):
#     """
#     Retrieve, update or delete a special date.
#     """

#     permission_classes = [IsAuthenticated]

#     def get_object(self, pk, user):
#         try:
#             return SpecialDate.objects.get(pk=pk, user=user)
#         except SpecialDate.DoesNotExist:
#             return None

#     @swagger_auto_schema(
#         operation_summary="Retrieve Special Date",
#         responses={200: SpecialDateSerializer}
#     )
#     def get(self, request, pk, *args, **kwargs):
#         special_date = self.get_object(pk, request.user)
#         if not special_date:
#             return error_response("Special date not found", status.HTTP_404_NOT_FOUND)

#         serializer = SpecialDateSerializer(special_date)
#         return success_response("Special date retrieved successfully", serializer.data)

#     # @swagger_auto_schema(
#     #     operation_summary="Update Special Date",
#     #     request_body=SpecialDateSerializer,
#     #     responses={200: SpecialDateSerializer}
#     # )
#     # def patch(self, request, pk, *args, **kwargs):
#     #     special_date = self.get_object(pk, request.user)
#     #     if not special_date:
#     #         return error_response("Special date not found", status.HTTP_404_NOT_FOUND)

#         # serializer = SpecialDateSerializer(
#         #     special_date, data=request.data, partial=True
#         # )
#         # if serializer.is_valid():
#         #     special_date = serializer.save()
#         #     return success_response(
#         #         "Special date updated successfully", serializer.data
#         #     )
#         # return error_response("Validation error", serializer.errors, 400)

#     @swagger_auto_schema(
#         operation_summary="Delete Special Date",
#         responses={204: "Deleted successfully"}
#     )
#     def delete(self, request, pk, *args, **kwargs):
#         special_date = self.get_object(pk, request.user)
#         if not special_date:
#             return error_response("Special date not found", status.HTTP_404_NOT_FOUND)

#         special_date.delete()
#         return success_response("Special date deleted successfully", None, 204)

# class UpdateWellbeingView(APIView):
#     """Log user's wellbeing score."""
#     @swagger_auto_schema(request_body=WellbeingScoreSerializer)
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         score = request.data.get("score")
#         if not score:
#             return Response(
#                 {"errors": ["Score is required"]}, status=status.HTTP_400_BAD_REQUEST
#             )
#         try:
#             score = int(score)
#             if not 0 <= score <= 10:
#                 raise ValueError
#         except (ValueError, TypeError):
#             return Response(
#                 {"errors": ["Score must be an integer between 0-10"]}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         WellbeingScore.objects.create(
#             user=request.user,
#             score=score,
#             score_date=timezone.now()
#         )
#         return Response(status=status.HTTP_200_OK)

# class LogActionView(APIView):
#     """Log application actions (authenticated or unauthenticated)."""
#     permission_classes = [AllowAny]  # Allow both authenticated and unauthenticated access

#     @swagger_auto_schema(request_body=ActionLogSerializer)
#     def post(self, request):
#         serializer = ActionLogSerializer(data=request.data)
#         if serializer.is_valid():
#             data = serializer.validated_data
#             user = None
#             token = data.get("token")
#             if token:
#                 try:
#                     # Ensure token is a string before converting to UUID
#                     token_str = str(token)
#                     token_uuid = uuid.UUID(token_str)
#                     login_entry = LastLogin.objects.get(
#                         token=token_uuid, token_valid=True
#                     )
#                     user = login_entry.user
#                 except (ValueError, LastLogin.DoesNotExist):
#                     pass

#             # Create the action log entry
#             ActionData.objects.create(
#                 user=user,
#                 action_date=timezone.now(),
#                 ip_address=request.META.get("REMOTE_ADDR", ""),
#                 application_area_name=data["application_area_name"],
#                 action_description=data["action_description"],
#                 action_duration_seconds=data["action_duration_seconds"]
#             )

#             # If the user is authenticated, update gamification data
#             if user:
#                 gamification_data, created = GamificationData.objects.get_or_create(user=user)

#                 # Award points for logging an action
#                 gamification_data.points += 10  # Example: 10 points per logged action
#                 gamification_data.save()

#                 # Update streak if the action is related to taking breaks
#                 if "break" in data["application_area_name"].lower():
#                     last_break = DateEntry.objects.filter(
#                         user=user, start_date__gte=timezone.now() - timezone.timedelta(days=1)
#                     ).order_by("-start_date").first()

#                     if last_break:
#                         gamification_data.streak_days += 1
#                     else:
#                         gamification_data.streak_days = 1  # Reset streak if no recent breaks
#                     gamification_data.save()

#                 # Award badges based on updated gamification data
#                 award_badges(user)

#             return Response(status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class UpdateProfileView(APIView):
#     """Update user profile details."""
#     @swagger_auto_schema(request_body=UserSerializer)

#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         user = request.user
#         data = request.data
#         user.first_name = data.get("first_name", user.first_name)
#         user.last_name = data.get("last_name", user.last_name)
#         user.full_name = data.get("full_name", user.full_name)
#         new_password = data.get("password")
#         if new_password:
#             try:
#                 from .validators import validate_password
#                 validate_password(new_password)
#                 user.set_password(new_password)
#             except ValueError as e:
#                 return Response(
#                     {"errors": [str(e)]}, status=status.HTTP_400_BAD_REQUEST
#                 )
#         user.email = data.get("email", user.email)
#         user.holiday_days = data.get("holiday_days", user.holiday_days)
#         user.birthday = data.get("birthday", user.birthday)
#         user.home_location_timezone = data.get(
#             "home_location_timezone", user.home_location_timezone
#         )
#         user.home_location_coordinates = data.get(
#             "home_location_coordinates", user.home_location_coordinates
#         )
#         user.working_days_per_week = data.get(
#             "working_days_per_week", user.working_days_per_week
#         )
#         user.save()
#         return Response({"success": True}, status=status.HTTP_200_OK)


########### UPDATE USER PROFILE ##################
############                    #################
# class UpdateProfileView(APIView):
#     """Update user profile details."""

#     @swagger_auto_schema(request_body=UserSerializer)
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response({
#                 "message": "Unauthorized",
#                 "status": False,
#                 "data": None,
#                 "errors": {"auth": "You must be logged in."}
#             }, status=status.HTTP_401_UNAUTHORIZED)

#         user = request.user
#         data = request.data.copy()

#         # Convert and validate birthday
#         birthday_str = data.get("birthday")
#         if birthday_str:
#             try:
#                 data["birthday"] = date_parser.isoparse(birthday_str)
#             except Exception:
#                 return Response({
#                     "message": "Invalid date format for birthday",
#                     "status": False,
#                     "data": None,
#                     "errors": {"birthday": "Use ISO format e.g. 2025-07-23T05:36:26Z"}
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         # Validate password (if provided)
#         new_password = data.get("password")
#         if new_password:
#             try:
#                 validate_password(new_password)
#                 user.set_password(new_password)
#                 user.save()
#             except (ValueError, DRFValidationError) as e:
#                 return Response({
#                     "message": "Password validation failed",
#                     "status": False,
#                     "data": None,
#                     "errors": {"password": str(e)}
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         # Validate other fields via serializer
#         serializer = UserSerializer(instance=user, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "message": "Profile updated successfully",
#                 "status": True,
#                 "data": serializer.data,
#                 "errors": None
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({
#                 "message": "Validation failed",
#                 "status": False,
#                 "data": None,
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)
        


# from django.utils import timezone
# from .tasks import sync_user_holidays
# from .utils import timezone_to_country_code

# class UpdateProfileView(APIView):
#     """Update user profile details."""

#     @swagger_auto_schema(request_body=UserSerializer)
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response({
#                 "message": "Unauthorized",
#                 "status": False,
#                 "data": None,
#                 "errors": {"auth": "You must be logged in."}
#             }, status=status.HTTP_401_UNAUTHORIZED)

#         user = request.user
#         data = request.data.copy()

#         # Convert and validate birthday
#         birthday_str = data.get("birthday")
#         if birthday_str:
#             try:
#                 data["birthday"] = date_parser.isoparse(birthday_str)
#             except Exception:
#                 return Response({
#                     "message": "Invalid date format for birthday",
#                     "status": False,
#                     "data": None,
#                     "errors": {"birthday": "Use ISO format e.g. 2025-07-23T05:36:26Z"}
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         # Validate password (if provided)
#         new_password = data.get("password")
#         if new_password:
#             try:
#                 validate_password(new_password)
#                 user.set_password(new_password)
#                 user.save()
#             except (ValueError, DRFValidationError) as e:
#                 return Response({
#                     "message": "Password validation failed",
#                     "status": False,
#                     "data": None,
#                     "errors": {"password": str(e)}
#                 }, status=status.HTTP_400_BAD_REQUEST)

#         # --- Track if user updates country/timezone ---
#         old_timezone = user.home_location_timezone
#         old_coords = user.home_location_coordinates

#         # Validate other fields via serializer
#         serializer = UserSerializer(instance=user, data=data, partial=True)
#         if serializer.is_valid():
#             updated_user = serializer.save()

#             timezone_changed = old_timezone != updated_user.home_location_timezone
#             coords_changed = old_coords != updated_user.home_location_coordinates

#             if timezone_changed or coords_changed:
#                 calendar = updated_user.holiday_calendar
#                 if calendar:
#                     # Infer country code from timezone
#                     country_code = timezone_to_country_code(updated_user.home_location_timezone)
#                     calendar.country_code = country_code
#                     calendar.last_synced = timezone.now()
#                     calendar.save(update_fields=["country_code", "last_synced"])

#                     # Trigger Celery sync
#                     sync_user_holidays.delay(updated_user.id, calendar.country_code)

#             return Response({
#                 "message": "Profile updated successfully",
#                 "status": True,
#                 "data": serializer.data,
#                 "errors": None
#             }, status=status.HTTP_200_OK)

#         else:
#             return Response({
#                 "message": "Validation failed",
#                 "status": False,
#                 "data": None,
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)











# class UpdateSettingsView(APIView):
#     """Update user settings JSON."""
#     @swagger_auto_schema(request_body=UpdateSettingsSerializer)
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         settings_json = request.data.get("settings_json")
#         if not settings_json:
#             return Response(
#                 {"errors": ["Settings JSON is required"]}, 
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#         # Ensure a default value is provided for settings_json
#         user_settings, created = UserSettings.objects.get_or_create(
#             user=request.user,
#             defaults={"settings_json": {}},  # Default empty JSON object
#         )
#         user_settings.settings_json = settings_json
#         user_settings.save()
#         return Response(status=status.HTTP_200_OK)

# class GetSettingsView(APIView):
#     """Retrieve user settings JSON."""
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         try:
#             settings = UserSettings.objects.get(user=request.user)
#             return Response(
#                 {"settings_json": settings.settings_json}, 
#                 status=status.HTTP_200_OK
#             )
#         except UserSettings.DoesNotExist:
#             return Response(
#                 {"settings_json": None}, status=status.HTTP_200_OK
#             )
        
# class GetOnboardingDataView(APIView):
#     """Retrieve user's onboarding data."""
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         try:
#             onboarding_data = OnboardingData.objects.get(user=request.user)
#             serializer = OnboardingDataSerializer(onboarding_data)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except OnboardingData.DoesNotExist:
#             return Response(
#                 {"detail": "Onboarding data not found"}, status=status.HTTP_404_NOT_FOUND
#             )


# class UpdateOnboardingDataView(APIView):
#     """Update or create user's onboarding data."""
#     @swagger_auto_schema(request_body=OnboardingDataSerializer)
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         survey_results = request.data.get("survey_results")
#         if not survey_results:
#             return Response(
#                 {"errors": ["Survey results are required"]}, status=status.HTTP_400_BAD_REQUEST
#             )
#         # Update or create the onboarding data
#         onboarding_data, created = OnboardingData.objects.update_or_create(
#             user=request.user,
#             defaults={"survey_results": survey_results},
#         )
#         serializer = OnboardingDataSerializer(onboarding_data)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    


# class OptimizationScoreView(APIView):
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

#         # Step 1: Calculate the average wellbeing score over the last 7 days
#         recent_scores = WellbeingScore.objects.filter(
#             user=request.user,
#             score_date__gte=timezone.now() - timedelta(days=7)
#         ).aggregate(avg_score=Avg("score"))
#         avg_wellbeing_score = recent_scores["avg_score"] or 0  # Default to 0 if no scores exist

#         # Step 2: Count upcoming events in the next 30 days
#         upcoming_events_count = DateEntry.objects.filter(
#             user=request.user,
#             start_date__gte=timezone.now(),
#             start_date__lte=timezone.now() + timedelta(days=30)
#         ).count()

#         # Step 3: Check for blackout dates in the next 30 days
#         blackout_dates = BlackoutDate.objects.filter(
#             user=request.user,
#             start_date__gte=timezone.now(),
#             start_date__lte=timezone.now() + timedelta(days=30)
#         )

#         # Step 4: Fetch public holidays in the next 30 days
#         public_holidays = PublicHoliday.objects.filter(
#             user=request.user,
#             date__gte=timezone.now().date(),
#             date__lte=(timezone.now() + timedelta(days=30)).date()
#         )

#         # Step 5: Calculate the optimization score
#         event_load_penalty = upcoming_events_count * 0.5  # Penalize for too many events
#         public_holiday_bonus = len(public_holidays) * 2  # Bonus for public holidays
#         optimization_score = avg_wellbeing_score - event_load_penalty + public_holiday_bonus

#         # Step 6: Return the result
#         return Response(
#             {
#                 "optimization_score": round(optimization_score, 2),
#                 "details": {
#                     "average_wellbeing_score": avg_wellbeing_score,
#                     "upcoming_events_count": upcoming_events_count,
#                     "public_holidays_count": len(public_holidays),
#                     "blackout_dates": [
#                         {"start_date": bd.start_date, "end_date": bd.end_date}
#                         for bd in blackout_dates
#                     ],
#                 },
#             },
#             status=status.HTTP_200_OK,
        # )
    
# class GamificationDataView(APIView):
#     """Retrieve gamification data for the authenticated user."""

#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response({
#                 "message": "Unauthorized",
#                 "status": False,
#                 "data": None,
#                 "errors": {"detail": "User is not authenticated."}
#             }, status=status.HTTP_401_UNAUTHORIZED)

#         gamification_data, _ = GamificationData.objects.get_or_create(user=request.user)
#         smart_planning_score = calculate_smart_planning_score(request.user)

#         return Response({
#             "message": "Gamification data retrieved successfully.",
#             "status": True,
#             "data": {
#                 "points": gamification_data.points,
#                 "streak_days": gamification_data.streak_days,
#                 "badges": gamification_data.badges,
#                 "smart_planning_score": smart_planning_score,
#             },
#             "errors": None
#         }, status=status.HTTP_200_OK)
    

# class UpdateWellbeingView(APIView):
#     """Log user's wellbeing score and update gamification data."""

#     @swagger_auto_schema(request_body=WellbeingScoreSerializer)
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response({
#                 "message": "Unauthorized",
#                 "status": False,
#                 "data": None,
#                 "errors": {"detail": "User is not authenticated."}
#             }, status=status.HTTP_401_UNAUTHORIZED)

#         score = request.data.get("score")
#         score_type = request.data.get("score_type")

#         if not score or not score_type:
#             return Response({
#                 "message": "Validation failed.",
#                 "status": False,
#                 "data": None,
#                 "errors": {
#                     "score": "This field is required." if not score else "",
#                     "score_type": "This field is required." if not score_type else ""
#                 }
#             }, status=status.HTTP_400_BAD_REQUEST)

#         wellbeing = WellbeingScore.objects.create(
#             user=request.user,
#             score=score,
#             score_type=score_type,
#             score_date=timezone.now()
#         )

#         # Update gamification data
#         gamification_data, _ = GamificationData.objects.get_or_create(user=request.user)
#         gamification_data.points += 20  # Award 20 points
#         gamification_data.save()

#         # Award badges
#         award_badges(request.user)

#         return Response({
#             "message": "Wellbeing score logged successfully.",
#             "status": True,
#             "data": {
#                 "score": wellbeing.score,
#                 "score_type": wellbeing.score_type,
#                 "score_date": wellbeing.score_date
#             },
#             "errors": None
#         }, status=status.HTTP_200_OK)
 
# class SuggestedDatesView(APIView):
#     """Generate suggested holidays and incorporate weather data."""
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
#         # Step 1: Generate holiday suggestions using BetterBreaksAI
#         holiday_suggestions = generate_holiday_suggestions(request.user)

#         # Step 2: Fetch user's coordinates
#         if request.user.home_location_coordinates:
#             try:
#                 latitude, longitude = request.user.home_location_coordinates.split(",")
#                 latitude = float(latitude.strip())
#                 longitude = float(longitude.strip())

#                 # Step 3: Adjust scores based on weather data
#                 for suggestion in holiday_suggestions:
#                     start_date = suggestion["start_date"].date()  # Extract date from datetime
#                     try:
#                         weather_data = fetch_weather_data(latitude, longitude, start_date)
#                         suggestion["score"] = adjust_score_based_on_weather(suggestion["score"], weather_data)
#                     except Exception as e:
#                         # Optionally log or ignore errors fetching weather
#                         pass
#             except Exception as e:
#                 # Handle invalid home_location_coordinates format gracefully
#                 pass  # Skip weather adjustment

#         # Step 4: Return the final list of suggestions
#         return Response(
#             {
#                 "suggestions": [
#                     {
#                         "start_date": s["start_date"].isoformat(),
#                         "end_date": s["end_date"].isoformat(),
#                         "title": s["title"],
#                         "description": s["description"],
#                         "score": s["score"],
#                     }
#                     for s in holiday_suggestions
#                 ]
#             },
#             status=status.HTTP_200_OK,
#         )
    

# class AddDateView(APIView):
#     @swagger_auto_schema(request_body=DateEntrySerializer)
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

#         serializer = DateEntrySerializer(data=request.data)
#         if serializer.is_valid():
#             date_entry = serializer.save(user=request.user)
#             return Response({"uuid": date_entry.id}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# class DeleteDateView(APIView):
#     def delete(self, request, date_uuid):
#         if not request.user.is_authenticated:
#             return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

#         try:
#             date_entry = DateEntry.objects.get(id=date_uuid, user=request.user)
#             date_entry.delete()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         except DateEntry.DoesNotExist:
#             return Response({"error": "Date not found"}, status=status.HTTP_404_NOT_FOUND)
        



# # class WellbeingQuestionView(APIView):
# #     def get(self, request):
# #         questions = WellbeingQuestion.objects.all()
# #         serializer = WellbeingQuestionSerializer(questions, many=True)
# #         return Response(serializer.data, status=status.HTTP_200_OK)
    

#     ############### BLACKOUT DATE VIEWS #####################
# ######################################################## 
# class BlackoutDatesView(APIView):
#     """Retrieve authenticated user's blackout dates."""
#     def get(self, request):
#         if not request.user.is_authenticated:
#             return Response(
#                 {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
#             )
#         blackout_dates = BlackoutDate.objects.filter(user=request.user)
#         serializer = BlackoutDateSerializer(blackout_dates, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
# # --------------BLACKOUT DATES ------------------
# class AddBlackoutDateView(APIView):
#     @swagger_auto_schema(request_body=BlackOutDateSerializer)
#     def post(self, request):
#         if not request.user.is_authenticated:
#             return error_response(message="An error occured ", errors= "Unauthorized user", status_code=status.HTTP_401_UNAUTHORIZED)

#         serializer = BlackOutDateSerializer(data=request.data)
#         if serializer.is_valid():
#             blackout_date = serializer.save(user=request.user)
#             return success_response(
#                 message="Blackout date added succesfully",
#                 data=serializer.data,
#                 status_code=status.HTTP_201_CREATED
#             )
#         return error_response(
#             message="An error occured",
#             errors=serializer.errors,
#         )

# #------------DELETE BLACKOUT DATES-------------------
# class DeleteBlackoutDateView(APIView):
#     def delete(self, request, blackout_uuid):
#         if not request.user.is_authenticated:
#             return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

#         try:
#             blackout_date = BlackoutDate.objects.get(id=blackout_uuid, user=request.user)
#             blackout_date.delete()
#             return success_response(message="Blackout date successfully deleted",status_code=status.HTTP_204_NO_CONTENT)
#         except BlackoutDate.DoesNotExist:
#             return error_response(message="Blackout date not found", status_code=status.HTTP_404_NOT_FOUND)


# # --------------CREATE BREAK PLAN------------------

# class CreateBreakPlanView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(request_body=BreakPlanSerializer)
#     def post(self, request):
#         serializer = BreakPlanSerializer(data=request.data, context={"request": request})
#         if serializer.is_valid():
#             break_plan = serializer.save()
#             return Response({
#                 "message": "Break plan created successfully.",
#                 "status": True,
#                 "data": BreakPlanSerializer(break_plan).data,
#                 "errors": None
#             }, status=status.HTTP_201_CREATED)

#         return Response({
#             "message": "Invalid input.",
#             "status": False,
#             "data": None,
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)


# class UpcomingBreaksView(APIView):
#     """
#     Get upcoming breaks for the logged-in user,
#     respecting user's home_location_timezone.
#     """

#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         today = now().date()

#         breaks = (
#             BreakPlan.objects.filter(
#                 user=user,
#                 startDate__date__gte=today,
#                 status="approved"   # only approved breaks
#             ).order_by("startDate")
#         )

#         if not breaks.exists():
#             return success_response(
#                 message="No upcoming approved breaks found",
#                 data=[]
#             )

#         serializer = BreakPlanSerializer(breaks, many=True)
#         return success_response(
#             message="Fetched upcoming approved breaks successfully",
#             data=serializer.data
#         )


# class ListUserBreakPlansView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         manual_parameters=[
#             openapi.Parameter(
#                 'status', openapi.IN_QUERY,
#                 description="Status of the break plan (planned|pending|approved|rejected)",
#                 type=openapi.TYPE_STRING
#             ),
#             openapi.Parameter(
#                 'year', openapi.IN_QUERY,
#                 description="Year to filter break plans by start date",
#                 type=openapi.TYPE_INTEGER
#             ),
#             openapi.Parameter(
#                 'limit', openapi.IN_QUERY,
#                 description="Number of items per page",
#                 type=openapi.TYPE_INTEGER
#             ),
#             openapi.Parameter(
#                 'offset', openapi.IN_QUERY,
#                 description="Offset for pagination (default 0)",
#                 type=openapi.TYPE_INTEGER
#             )
#         ]
#     )
#     def get(self, request):
#         user = request.user
#         status_param = request.query_params.get("status")
#         year_param = request.query_params.get("year")
#         limit = request.query_params.get("limit")
#         offset = request.query_params.get("offset")

#         try:
#             # Initial Query
#             plans_qs = BreakPlan.objects.filter(user=user)

#             # Optional filters
#             if status_param:
#                 plans_qs = plans_qs.filter(status=status_param)

#             if year_param:
#                 try:
#                     year = int(year_param)
#                     plans_qs = plans_qs.filter(startDate__year=year)
#                 except ValueError:
#                     return Response({
#                         "message": "Invalid year format.",
#                         "status": False,
#                         "data": None,
#                         "errors": {"year": ["Must be a valid integer"]}
#                     }, status=status.HTTP_400_BAD_REQUEST)

#             plans_qs = plans_qs.order_by("-created_at")

#             limit = int(limit) if limit else 10
#             offset = int(offset) if offset else 0

#             paginator = Paginator(plans_qs, limit)
#             page_number = (offset // limit) + 1

#             if page_number > paginator.num_pages:
#                 return Response({
#                     "message": "No more results.",
#                     "status": True,
#                     "data": {
#                         "plans": [],
#                         "total": paginator.count,
#                         "hasMore": False
#                     },
#                     "errors": None
#                 }, status=status.HTTP_200_OK)

#             current_page = paginator.page(page_number)
#             serialized = BreakPlanListSerializer(current_page.object_list, many=True)

#             return Response({
#                 "message": "Break plans retrieved successfully.",
#                 "status": True,
#                 "data": {
#                     "plans": serialized.data,
#                     "total": paginator.count,
#                     "hasMore": current_page.has_next()
#                 },
#                 "errors": None
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({
#                 "message": "An unexpected error occurred.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"server": [str(e)]}
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # --------------UPDATE BREAK PLAN------------------
# # Very high possibility i deprecate this view in future

# class UpdateBreakPlanView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         request_body=BreakPlanUpdateSerializer,
#         operation_description="Update a break plan. When a break plan is approved, gamification rewards are automatically created.",
#         responses={
#             200: openapi.Response(
#                 description="Break plan updated successfully with gamification rewards if approved",
#                 examples={
#                     "application/json": {
#                         "message": "Break plan updated successfully.",
#                         "status": True,
#                         "data": {
#                             "plan": {
#                                 "id": "uuid-string",
#                                 "startDate": "2023-06-01T00:00:00Z",
#                                 "endDate": "2023-06-07T00:00:00Z",
#                                 "description": "Summer vacation",
#                                 "status": "approved",
#                                 "updatedAt": "2023-05-15T14:30:00Z"
#                             },
#                             "gamification": {
#                                 "break_score": {
#                                     "id": 1,
#                                     "score_date": "2023-06-01",
#                                     "score_value": 10,
#                                     "frequency_points": 5,
#                                     "adherence_points": 5,
#                                     "wellbeing_impact": "positive",
#                                     "break_type": "vacation",
#                                     "notes": "Break plan approved"
#                                 },
#                                 "streak": {
#                                     "id": 1,
#                                     "current_streak": 1,
#                                     "longest_streak": 1,
#                                     "streak_period": "monthly"
#                                 },
#                                 "recent_badges": [
#                                     {
#                                         "id": 1,
#                                         "badge_type": "consistent_breaker",
#                                         "level": 1,
#                                         "description": "Took your first break!"
#                                     }
#                                 ]
#                             }
#                         },
#                         "errors": None
#                     }
#                 }
#             ),
#             400: openapi.Response(description="Invalid input"),
#             404: openapi.Response(description="Break plan not found"),
#             500: openapi.Response(description="Server error")
#         }
#     )
#     def put(self, request, planId):
#         try:
#             user = request.user

#             if user.is_superuser or getattr(user, 'role', None) == 'admin':
#                 plan = get_object_or_404(BreakPlan, id=planId)
#             else:
#                 plan = get_object_or_404(BreakPlan, id=planId, user=user)

#             serializer = BreakPlanUpdateSerializer(plan, data=request.data)
#             if serializer.is_valid():
#                 updated_plan = serializer.save()
                
#                 # Check if plan was approved and include gamification info
#                 gamification_data = None
#                 if updated_plan.status == 'approved':
#                     # Get gamification data for the user
#                     break_scores = BreakScore.objects.filter(user=user).order_by('-created_at')[:1]
#                     streak_scores = StreakScore.objects.filter(user=user).order_by('-updated_at')[:1]
#                     badges = Badge.objects.filter(user=user).order_by('-created_at')[:3]
                    
#                     gamification_data = {
#                         "break_score": BreakScoreSerializer(break_scores[0]).data if break_scores else None,
#                         "streak": StreakScoreSerializer(streak_scores[0]).data if streak_scores else None,
#                         "recent_badges": BadgeSerializer(badges, many=True).data if badges else [],
#                     }
                
#                 return Response({
#                     "message": "Break plan updated successfully.",
#                     "status": True,
#                     "data": {
#                         "plan": {
#                             "id": str(updated_plan.id),
#                             "startDate": updated_plan.startDate,
#                             "endDate": updated_plan.endDate,
#                             "description": updated_plan.description,
#                             "status": updated_plan.status,
#                             "updatedAt": updated_plan.updated_at,
#                         },
#                         "gamification": gamification_data
#                     },
#                     "errors": None
#                 }, status=status.HTTP_200_OK)

#             return Response({
#                 "message": "Validation failed.",
#                 "status": False,
#                 "data": None,
#                 "errors": serializer.errors
#             }, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             traceback.print_exc()
#             logger.error(f"BreakPlan update error: {str(e)}")

#             return Response({
#                 "message": "An unexpected error occurred.",
#                 "status": False,
#                 "data": None,
#                 "errors": {
#                     "server": [str(e)]
#                 }
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# class DeleteBreakPlanView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         operation_description="Delete a break plan by its ID. Only the owner or an admin can perform this action.",
#         manual_parameters=[
#             openapi.Parameter(
#                 'planId',
#                 openapi.IN_PATH,
#                 description="ID of the break plan to delete",
#                 type=openapi.TYPE_STRING,
#                 required=True
#             ),
#         ],
#         responses={
#             200: openapi.Response(
#                 description="Break plan deleted successfully.",
#                 examples={
#                     "application/json": {
#                         "message": "Break plan deleted successfully.",
#                         "status": True,
#                         "data": None,
#                         "errors": None
#                     }
#                 }
#             ),
#             403: openapi.Response(
#                 description="Forbidden - Not authorized to delete this plan."
#             ),
#             404: openapi.Response(
#                 description="Break plan not found."
#             ),
#             500: openapi.Response(
#                 description="Unexpected server error."
#             ),
#         }
#     )
#     def delete(self, request, planId):
#         user = request.user

#         try:
#             plan = BreakPlan.objects.get(id=planId)
#         except BreakPlan.DoesNotExist:
#             return Response({
#                 "message": "Break plan not found.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"planId": ["Invalid plan ID"]}
#             }, status=status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             return Response({
#                 "message": "An unexpected error occurred.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"server": [str(e)]}
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         if not (user.is_superuser or user.is_staff or getattr(user, 'role', '') == 'admin' or plan.user == user):
#             return Response({
#                 "message": "You do not have permission to delete this plan.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"permission": "Not authorized"}
#             }, status=status.HTTP_403_FORBIDDEN)

#         try:
#             plan.delete()
#             return Response({
#                 "message": "Break plan deleted successfully.",
#                 "status": True,
#                 "data": None,
#                 "errors": None
#             }, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({
#                 "message": "An error occurred while deleting the break plan.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"server": [str(e)]}
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# # =============USER SETTINGS=============

# class UserSettingsView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(
#         responses={200: UserSettingsSerializer()},
#         operation_description="Get the authenticated user's app settings"
#     )
#     def get(self, request):
#         user = request.user
#         settings_obj, _ = UserSettings.objects.get_or_create(user=user)
#         serializer = UserSettingsSerializer(settings_obj)
#         return Response({
#             "message": "Settings retrieved successfully.",
#             "status": True,
#             "data": serializer.data,
#             "errors": None
#         }, status=status.HTTP_200_OK)

#     @swagger_auto_schema(
#         request_body=UserSettingsSerializer,
#         responses={200: openapi.Response(description="Settings updated successfully")}
#     )
#     def put(self, request):
#         user = request.user
#         settings_obj, _ = UserSettings.objects.get_or_create(user=user)

#         serializer = UserSettingsSerializer(settings_obj, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "message": "Settings updated successfully.",
#                 "status": True,
#                 "data": None,
#                 "errors": None
#             }, status=status.HTTP_200_OK)

#         return Response({
#             "message": "Validation failed.",
#             "status": False,
#             "data": None,
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)

# #  ======== USER NOTIFICATION API VIEW ========
# class NotificationPreferenceView(APIView):
#     permission_classes = [IsAuthenticated]

#     @swagger_auto_schema(responses={200: NotificationPreferenceSerializer})
#     def get(self, request):
#         user = request.user
#         preferences, created = UserNotificationPreference.objects.get_or_create(user=user)
#         serializer = NotificationPreferenceSerializer(preferences)

#         return Response({
#             "success": True,
#             "preferences": serializer.data
#         }, status=status.HTTP_200_OK)

#     @swagger_auto_schema(request_body=NotificationPreferenceSerializer)
#     def put(self, request):
#         user = request.user
#         preferences, _ = UserNotificationPreference.objects.get_or_create(user=user)
#         serializer = NotificationPreferenceSerializer(preferences, data=request.data)

#         if serializer.is_valid():
#             serializer.save()
#             return Response({
#                 "success": True,
#                 "message": "Notification preferences updated successfully"
#             }, status=status.HTTP_200_OK)

#         return Response({
#             "success": False,
#             "message": "Validation failed",
#             "errors": serializer.errors,
#             "data": None
#         }, status=status.HTTP_400_BAD_REQUEST)



# ###### SCHEDULE #####################################
# class ScheduleView(APIView):
#     """
#     Combined view to GET or POST WorkingPattern, BlackoutDates, and OptimizationGoals
#     """

#     @schedule_get_schema
#     def get(self, request):
#         user = request.user
#         try:
#             working_pattern = WorkingPattern.objects.filter(user=user).first()
#             blackout_dates = BlackoutDate.objects.filter(user=user)
#             optimization_goals = OptimizationGoal.objects.filter(user=user)

#             data = {
#                 "working_pattern": WorkingPatternSerializer(working_pattern).data if working_pattern else None,
#                 "blackout_dates": BlackOutDateSerializer(blackout_dates, many=True).data,
#                 "optimization_goals": OptimizationGoalSerializer(optimization_goals, many=True).data,
#             }

#             return Response({
#                 "message": "Schedule retrieved successfully.",
#                 "status": True,
#                 "data": data,
#                 "errors": None
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({
#                 "message": "Internal server error.",
#                 "status": False,
#                 "data": None,
#                 "errors": {
#                     "non_field_errors": [str(e)],
#                     "traceback": traceback.format_exc().splitlines()
#                 }
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#     @schedule_post_schema
#     def post(self, request):
#         user = request.user
#         data = request.data

#         try:
#             with transaction.atomic():
#                 # === WORKING PATTERN ===
#                 wp_data = data.get('working_pattern')
#                 if wp_data:
#                     wp_instance, _ = WorkingPattern.objects.get_or_create(user=user)
#                     wp_serializer = WorkingPatternSerializer(wp_instance, data=wp_data, partial=True)
#                     wp_serializer.is_valid(raise_exception=True)
#                     wp_serializer.save()

#                 # === BLACKOUT DATES ===
#                 blackout_data = data.get('blackout_dates', [])
#                 BlackoutDate.objects.filter(user=user).delete()
#                 if blackout_data:
#                     blackout_serializer = BlackOutDateSerializer(
#                         data=blackout_data,
#                         many=True,
#                         context={"request": request}
#                     )
#                     blackout_serializer.is_valid(raise_exception=True)
#                     blackout_serializer.save()

#                 # === OPTIMIZATION GOALS ===
#                 OptimizationGoal.objects.filter(user=user).delete()
#                 goal_data = data.get('optimization_goals', [])
#                 goal_objects = [OptimizationGoal(user=user, preference=pref) for pref in goal_data]
#                 OptimizationGoal.objects.bulk_create(goal_objects)

#                 return Response({
#                     "message": "Schedule updated successfully.",
#                     "status": True,
#                     "data": None,
#                     "errors": None
#                 }, status=status.HTTP_200_OK)

#         except DRFValidationError as ve:
#             return Response({
#                 "message": "Validation failed.",
#                 "status": False,
#                 "data": None,
#                 "errors": ve.detail
#             }, status=status.HTTP_400_BAD_REQUEST)

#         except IntegrityError as ie:
#             return Response({
#                 "message": "Database integrity error.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"non_field_errors": [str(ie)]}
#             }, status=status.HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             return Response({
#                 "message": "An unexpected error occurred.",
#                 "status": False,
#                 "data": None,
#                 "errors": {
#                     "non_field_errors": [str(e)],
#                     "traceback": traceback.format_exc().splitlines()
#                 }
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ######### MOOD CHECKIN ############
# class MoodCheckInView(APIView):
#     permission_classes = [IsAuthenticated]
#     @mood_checkin_schema
#     def post(self, request):
#         serializer = MoodCheckInSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(user=request.user)
#             return Response({
#                 "message": "Mood check-in successful",
#                 "status": True,
#                 "data": serializer.data,
#                 "errors": None
#             }, status=status.HTTP_201_CREATED)
#         return Response({
#             "message": "Validation error",
#             "status": False,
#             "data": None,
#             "errors": serializer.errors
#         }, status=status.HTTP_400_BAD_REQUEST)


# class MoodHistoryView(APIView):
#     permission_classes = [IsAuthenticated]
#     @mood_history_schema
#     def get(self, request):
#         start_date_str = request.query_params.get("start_date")
#         end_date_str = request.query_params.get("end_date")

#         moods = Mood.objects.filter(user=request.user)

#         if start_date_str:
#             start_date = parse_date(start_date_str)
#             if start_date:
#                 moods = moods.filter(created_at__date__gte=start_date)

#         if end_date_str:
#             end_date = parse_date(end_date_str)
#             if end_date:
#                 moods = moods.filter(created_at__date__lte=end_date)

#         serializer = MoodHistorySerializer(moods, many=True)
#         return Response({
#             "message": "Mood history retrieved successfully",
#             "status": True,
#             "data": serializer.data,
#             "errors": None
#         }, status=status.HTTP_200_OK)
    

# ######## FIRST LOGIN SETUP(ONBOARDING) ################

# @first_login_setup_docs
# class FirstLoginSetupView(APIView):
#     """
#     Create LeaveBalance, Preferences, and optional BreakPlan for user
#     if they don't already exist.
#     """

#     @swagger_auto_schema(
#         operation_summary="First Login Setup",
#         operation_description="Initial setup for LeaveBalance, Preferences, and optional BreakPlan.",
#         request_body=FirstLoginSetupSerializer,
#         responses={
#             status.HTTP_201_CREATED: openapi.Response(
#                 description="Setup completed successfully"
#             ),
#             status.HTTP_400_BAD_REQUEST: "Validation error",
#             status.HTTP_409_CONFLICT: "Duplicate or unique constraint violation",
#             status.HTTP_500_INTERNAL_SERVER_ERROR: "Server error"
#         }
#     )

#     def post(self, request, *args, **kwargs):
#         try:
#             serializer = FirstLoginSetupSerializer(
#                 data=request.data, context={"request": request}
#             )

#             if serializer.is_valid():
#                 user = request.user
#                 data = serializer.validated_data

#                 # --- Handle LeaveBalance ---
#                 lb_data = data.get("LeaveBalance")
#                 existing_leave_balance = LeaveBalance.objects.filter(user=user).first()

#                 if existing_leave_balance:
#                     lb_serializer = LeaveBalanceSerializer(
#                         existing_leave_balance,
#                         data=lb_data,
#                         partial=True,
#                         context={"request": request},
#                     )
#                 else:
#                     lb_serializer = LeaveBalanceSerializer(
#                         data=lb_data, context={"request": request}
#                     )

#                 if lb_serializer.is_valid():
#                     leave_balance = lb_serializer.save(user=user)
#                 else:
#                     return error_response(
#                         message="LeaveBalance validation failed",
#                         errors=lb_serializer.errors,
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # --- Handle BreakPreferences ---
#                 pref_data = data.get("BreakPreferences")
#                 existing_preferences = BreakPreferences.objects.filter(user=user).first()

#                 if existing_preferences:
#                     pref_serializer = BreakPreferencesSerializer(
#                         existing_preferences,
#                         data=pref_data,
#                         partial=True,
#                         context={"request": request},
#                     )
#                 else:
#                     pref_serializer = BreakPreferencesSerializer(
#                         data=pref_data, context={"request": request}
#                     )

#                 if pref_serializer.is_valid():
#                     preferences = pref_serializer.save(user=user)
#                 else:
#                     return error_response(
#                         message="BreakPreferences validation failed",
#                         errors=pref_serializer.errors,
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                     )

#                 # --- Handle BreakPlan ---
#                 bp_data = data.get("BreakPlan")
#                 existing_break_plan = BreakPlan.objects.filter(user=user).first()
                
#                 if existing_break_plan:
#                     # Update the existing plan
#                     bp_serializer = BreakPlanSerializer(
#                         existing_break_plan,
#                         data=bp_data,
#                         partial=True,
#                         context={"request": request},
#                     )
#                 else:
#                     # Create a new one
#                     bp_serializer = BreakPlanSerializer(
#                         data=bp_data,
#                         context={"request": request},
#                     )
                
#                 if bp_serializer.is_valid():
#                     break_plan = bp_serializer.save(user=user, leave_balance=leave_balance)
#                 else:
#                     return error_response(
#                         message="BreakPlan validation failed",
#                         errors=bp_serializer.errors,
#                         status_code=status.HTTP_400_BAD_REQUEST,
#                     )

#                 return success_response(
#                     message="First login setup completed successfully",
#                     data={
#                         "LeaveBalance": LeaveBalanceSerializer(
#                             leave_balance, context={"request": request}
#                         ).data,
#                         "BreakPreferences": BreakPreferencesSerializer(
#                             preferences, context={"request": request}
#                         ).data,
#                         "BreakPlan": BreakPlanSerializer(
#                             break_plan, context={"request": request}
#                         ).data,
#                     },
#                 )

#             return error_response(
#                 message="Invalid data",
#                 errors=serializer.errors,
#                 status_code=status.HTTP_400_BAD_REQUEST,
#             )

#         except Exception as e:
#             return error_response(
#                 message=f"An unexpected error occurred: {str(e)}",
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             )

#     # def post(self, request):
#     #     user = request.user
#     #     serializer = FirstLoginSetupSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     data = serializer.validated_data

#     #     # Check if user already has records and update them instead of creating new ones
#     #     existing_leave_balance = LeaveBalance.objects.filter(user=user).first()
#     #     existing_preferences = BreakPreferences.objects.filter(user=user).first()

#     #     try:
#     #         with transaction.atomic():
#     #             # 1. Leave Balance - update if exists, create if not
#     #             lb_data = data.get("LeaveBalance")
#     #             if existing_leave_balance:
#     #                 # Update existing leave balance
#     #                 lb_serializer = LeaveBalanceSerializer(existing_leave_balance, data=lb_data, partial=True)
#     #                 lb_serializer.is_valid(raise_exception=True)
#     #                 leave_balance = lb_serializer.save()
#     #             else:
#     #                 # Create new leave balance
#     #                 lb_serializer = LeaveBalanceSerializer(data=lb_data)
#     #                 lb_serializer.is_valid(raise_exception=True)
#     #                 leave_balance = lb_serializer.save(user=user)

#     #             # 2. Preferences - update if exists, create if not
#     #             pref_data = data.get("Preferences")
#     #             if existing_preferences:
#     #                 # Update existing preferences
#     #                 pref_serializer = BreakPreferencesSerializer(existing_preferences, data=pref_data, partial=True)
#     #                 pref_serializer.is_valid(raise_exception=True)
#     #                 preferences = pref_serializer.save()
#     #             else:
#     #                 # Create new preferences
#     #                 pref_serializer = BreakPreferencesSerializer(data=pref_data)
#     #                 pref_serializer.is_valid(raise_exception=True)
#     #                 preferences = pref_serializer.save(user=user)

#     #             # 3. Break Plan (optional)
#     #             break_plan = None
#     #             if data.get("BreakPlan"):
#     #                 bp_serializer = BreakPlanSerializer(data=data.get("BreakPlan"))
#     #                 bp_serializer.is_valid(raise_exception=True)
#     #                 break_plan = bp_serializer.save(user=user, leave_balance=leave_balance)

#     #         response_status = status.HTTP_200_OK if (existing_leave_balance or existing_preferences) else status.HTTP_201_CREATED
#     #         action_message = "updated" if (existing_leave_balance or existing_preferences) else "created"
            
#     #         return success_response(
#     #             message=f"First login setup {action_message} successfully",
#     #             data={
#     #                 "leave_balance": lb_serializer.data,
#     #                 "preferences": pref_serializer.data,
#     #                 "break_plan": BreakPlanSerializer(break_plan).data if break_plan else None
#     #             },
#     #             status_code=response_status
#     #         )

#     #     except IntegrityError as e:
#     #         # This should rarely happen now since we're handling existing records
#     #         error_msg = str(e)
#     #         if "core_leavebalance" in error_msg:
#     #             return error_response("Error updating leave balance. Please try again.", status_code=status.HTTP_400_BAD_REQUEST)
#     #         elif "core_breakpreferences" in error_msg:
#     #             return error_response("Error updating break preferences. Please try again.", status_code=status.HTTP_400_BAD_REQUEST)
#     #         else:
#     #             return error_response(f"Error during onboarding setup: {error_msg}", status_code=status.HTTP_400_BAD_REQUEST)
#     #     except DRFValidationError as e:
#     #         # Handle validation errors from serializers
#     #         return error_response(f"Validation error: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
#     #     except DjangoValidationError as e:
#     #         # Handle Django validation errors
#     #         return error_response(f"Validation error: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)
#     #     except Exception as e:
#     #         return error_response(f"An unexpected error occurred: {str(e)}", status_code=status.HTTP_400_BAD_REQUEST)









#     # def post(self, request, *args, **kwargs):
#     #     user = request.user
#     #     payload = request.data
#     #     created_items = {}

#     #     try:
#     #         # === LEAVE BALANCE ===
#     #         if not hasattr(user, 'leave_balance'):
#     #             lb_data = payload.get('LeaveBalance', {})
#     #             lb_serializer = LeaveBalanceSerializer(data=lb_data)
#     #             lb_serializer.is_valid(raise_exception=True)
#     #             leave_balance = lb_serializer.save(user=user)
#     #             created_items['LeaveBalance'] = lb_serializer.data
#     #         else:
#     #             created_items['LeaveBalance'] = "Already exists"

#     #         # === PREFERENCES ===
#     #         if not user.break_preferences.exists():
#     #             pref_data = payload.get('Preferences', {})
#     #             pref_serializer = BreakPreferencesSerializer(data=pref_data)
#     #             pref_serializer.is_valid(raise_exception=True)
#     #             preferences = pref_serializer.save(user=user)
#     #             created_items['Preferences'] = pref_serializer.data
#     #         else:
#     #             created_items['Preferences'] = "Already exists"

#     #         # === BREAK PLAN ===
#     #         break_plan_data = payload.get('BreakPlan', {})
#     #         if break_plan_data.get('startDate') and break_plan_data.get('endDate'):
#     #             bp_serializer = BreakPlanSerializer(data=break_plan_data)
#     #             bp_serializer.is_valid(raise_exception=True)
#     #             break_plan = bp_serializer.save(
#     #                 user=user,
#     #                 leave_balance=user.leave_balance
#     #             )
#     #             created_items['BreakPlan'] = bp_serializer.data
#     #         else:
#     #             created_items['BreakPlan'] = "Not created - startDate & endDate required"

#     #         return success_response(
#     #             message="Setup complete",
#     #             data=created_items,
#     #             status_code=status.HTTP_201_CREATED
#     #         )

#     #     except IntegrityError as e:
#     #         return error_response(
#     #             message="Database integrity error",
#     #             errors=str(e),
#     #             status_code=status.HTTP_409_CONFLICT
#     #         )
#     #     except ValidationError as e:
#     #         return error_response(
#     #             message="Validation failed",
#     #             errors=e.detail,
#     #             status_code=status.HTTP_400_BAD_REQUEST
#     #         )
#     #     except Exception as e:
#     #         return error_response(
#     #             message="Unexpected server error",
#     #             errors=str(e),
#     #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#             # )

# class FirstLoginSetupUpdateView(APIView):
#     """
#     Update LeaveBalance, BreakPreferences, and/or BreakPlan for the logged-in user.
#     All fields are optional — only the provided ones will be updated.
#     """

#     @swagger_auto_schema(
#         operation_summary="Update First Login Setup Data",
#         operation_description="Update LeaveBalance, BreakPreferences, and/or BreakPlan. "
#                               "Each field is optional — only the provided ones will be updated.",
#         request_body=FirstLoginSetupDataSerializer,
#         responses={200: FirstLoginSetupDataSerializer}
#     )
#     def patch(self, request, *args, **kwargs):
#         user = request.user
#         serializer = FirstLoginSetupDataSerializer(data=request.data, context={"request": request})

#         if not serializer.is_valid():
#             return error_response(
#                 message="Invalid data",
#                 errors=serializer.errors,
#                 status_code=status.HTTP_400_BAD_REQUEST,
#             )

#         data = serializer.validated_data
#         updated = {}

#         # --- Update LeaveBalance if provided ---
#         lb_data = data.get("LeaveBalance")
#         if lb_data is not None:
#             leave_balance = LeaveBalance.objects.filter(user=user).first()
#             if leave_balance:
#                 lb_serializer = LeaveBalanceSerializer(
#                     leave_balance, data=lb_data, partial=True, context={"request": request}
#                 )
#                 if lb_serializer.is_valid(raise_exception=True):
#                     leave_balance = lb_serializer.save()
#                     updated["LeaveBalance"] = lb_serializer.data
#             else:
#                 lb_serializer = LeaveBalanceSerializer(
#                     data=lb_data, context={"request": request}
#                 )
#                 if lb_serializer.is_valid(raise_exception=True):
#                     leave_balance = lb_serializer.save(user=user)
#                     updated["LeaveBalance"] = lb_serializer.data

#         # --- Update BreakPreferences if provided ---
#         pref_data = data.get("BreakPreferences")
#         if pref_data is not None:
#             preferences = BreakPreferences.objects.filter(user=user).first()
#             if preferences:
#                 pref_serializer = BreakPreferencesSerializer(
#                     preferences, data=pref_data, partial=True, context={"request": request}
#                 )
#                 if pref_serializer.is_valid(raise_exception=True):
#                     preferences = pref_serializer.save()
#                     updated["BreakPreferences"] = pref_serializer.data
#             else:
#                 pref_serializer = BreakPreferencesSerializer(
#                     data=pref_data, context={"request": request}
#                 )
#                 if pref_serializer.is_valid(raise_exception=True):
#                     preferences = pref_serializer.save(user=user)
#                     updated["BreakPreferences"] = pref_serializer.data

#         # --- Update BreakPlan if provided ---
#         bp_data = data.get("BreakPlan")
#         if bp_data is not None:
#             break_plan = BreakPlan.objects.filter(user=user).first()
#             if break_plan:
#                 bp_serializer = BreakPlanSerializer(
#                     break_plan, data=bp_data, partial=True, context={"request": request}
#                 )
#                 if bp_serializer.is_valid(raise_exception=True):
#                     break_plan = bp_serializer.save()
#                     updated["BreakPlan"] = bp_serializer.data
#             else:
#                 bp_serializer = BreakPlanSerializer(
#                     data=bp_data, context={"request": request}
#                 )
#                 if bp_serializer.is_valid(raise_exception=True):
#                     break_plan = bp_serializer.save(user=user, leave_balance=user.leave_balance)
#                     updated["BreakPlan"] = bp_serializer.data

#         return success_response(
#             message="First login setup data updated successfully",
#             data=updated,
#         )


#         # --- Update BreakPreferences if provided ---
#         pref_data = data.get("BreakPreferences")
#         if pref_data is not None:
#             preferences = BreakPreferences.objects.filter(user=user).first()
#             if preferences:
#                 pref_serializer = BreakPreferencesSerializer(
#                     preferences, data=pref_data, partial=True, context={"request": request}
#                 )
#                 if pref_serializer.is_valid(raise_exception=True):
#                     preferences = pref_serializer.save()
#                     updated["BreakPreferences"] = pref_serializer.data
#             else:
#                 pref_serializer = BreakPreferencesSerializer(
#                     data=pref_data, context={"request": request}
#                 )
#                 if pref_serializer.is_valid(raise_exception=True):
#                     preferences = pref_serializer.save(user=user)
#                     updated["BreakPreferences"] = pref_serializer.data


# class FirstLoginSetupDataView(APIView):
#     """
#     Retrieve LeaveBalance, BreakPreferences, and BreakPlan for the logged-in user.
#     """

#     @swagger_auto_schema(
#         operation_summary="Retrieve First Login Setup Data",
#         operation_description="Fetch the user's LeaveBalance, BreakPreferences, and BreakPlan.",
#         responses={200: FirstLoginSetupDataSerializer}
#     )
#     def get(self, request, *args, **kwargs):
#         user = request.user

#         leave_balance = LeaveBalance.objects.filter(user=user).first()
#         preferences = BreakPreferences.objects.filter(user=user).first()
#         break_plan = BreakPlan.objects.filter(user=user).first()

#         if not leave_balance or not preferences:
#             return error_response(
#                 message="Setup data not found. Please complete first login setup.",
#                 status_code=status.HTTP_404_NOT_FOUND,
#             )

#         data = {
#             "LeaveBalance": LeaveBalanceSerializer(
#                 leave_balance, context={"request": request}
#             ).data if leave_balance else None,
#             "BreakPreferences": BreakPreferencesSerializer(
#                 preferences, context={"request": request}
#             ).data if preferences else None,
#             "BreakPlan": BreakPlanSerializer(
#                 break_plan, context={"request": request}
#             ).data if break_plan else None,
#         }

#         return success_response(
#             message="First login setup data retrieved successfully",
#             data=data,
#         )
#         # # --- Update BreakPlan if provided ---
#         # bp_data = data.get("BreakPlan")
#         # if bp_data is not None:
#         #     break_plan = BreakPlan.objects.filter(user=user).first()
#         #     if break_plan:
#         #         bp_serializer = BreakPlanSerializer(
#         #             break_plan, data=bp_data, partial=True, context={"request": request}
#         #         )
#         #         if bp_serializer.is_valid(raise_exception=True):
#         #             break_plan = bp_serializer.save()
#         #             updated["BreakPlan"] = bp_serializer.data
#         #     else:
#         #         bp_serializer = BreakPlanSerializer(
#         #             data=bp_data, context={"request": request}
#         #         )
#         #         if bp_serializer.is_valid(raise_exception=True):
#         #             break_plan = bp_serializer.save(user=user, leave_balance=user.leave_balance)
#         #             updated["BreakPlan"] = bp_serializer.data

#         # return success_response(
#         #     message="First login setup data updated successfully",
#         #     data=updated,
#         # )




# class WeatherForecastView(APIView):
#     @weather_forecast_schema
#     def get(self, request):
#         lat = request.query_params.get("lat")
#         lon = request.query_params.get("lon")
#         if not lat or not lon:
#             return Response({"detail": "lat and lon are required."}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             lat = float(lat)
#             lon = float(lon)
#         except ValueError:
#             return Response({"detail": "lat and lon must be valid numbers."}, status=status.HTTP_400_BAD_REQUEST)
#         forecast = fetch_6day_weather_forecast_openweathermap(lat, lon)
#         serializer = WeatherForecastDaySerializer(forecast, many=True)
#         return Response(serializer.data)




# #######################
# # ======= EVENTS & BOOKINGS =======
# #######################
# class EventListView(APIView):
#     permission_classes = [AllowAny]

#     @event_list_docs
#     def get(self, request):
#         events = Event.objects.all()

#         # Filters
#         title = request.query_params.get("title")
#         location = request.query_params.get("location")
#         start_date = request.query_params.get("start_date")
#         end_date = request.query_params.get("end_date")

#         if title:
#             events = events.filter(title__icontains=title)
#         if location:
#             events = events.filter(location__icontains=location)
#         if start_date and end_date:
#             events = events.filter(start_date__gte=start_date, end_date__lte=end_date)

#         serializer = EventSerializer(events, many=True)
#         return Response({
#             "message": "Events retrieved successfully",
#             "status": True,
#             "data": serializer.data,
#             "errors": None
#         }, status=status.HTTP_200_OK)


# class BookEventView(APIView):
#     permission_classes = [IsAuthenticated]

#     @book_event_docs
#     def post(self, request, event_id):
#         event = get_object_or_404(Event, id=event_id)
#         booking = Booking.objects.create(user=request.user, event=event)
#         serializer = BookingSerializer(booking)

#         return Response({
#             "message": "Event booked successfully. Proceed to payment.",
#             "status": True,
#             "data": serializer.data,
#             "errors": None
#         }, status=status.HTTP_201_CREATED)


# class InitiatePaymentView(APIView):
#     permission_classes = [IsAuthenticated]

#     @initiate_payment_docs
#     def post(self, request, booking_id):
#         try:
#             booking = Booking.objects.get(id=booking_id, user=request.user)
#         except Booking.DoesNotExist:
#             return Response({
#                 "message": "Booking not found.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"booking_id": "Invalid or unauthorized booking"}
#             }, status=404)

#         return PaystackGateway.initiate_payment(booking)


# class VerifyPaymentView(APIView):
#     permission_classes = [IsAuthenticated]

#     @verify_payment_docs
#     def post(self, request, booking_id):
#         reference = request.data.get("reference")
#         if not reference:
#             return Response({
#                 "message": "Payment reference is required.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"reference": "This field is required"}
#             }, status=400)

#         try:
#             booking = Booking.objects.get(id=booking_id, user=request.user)
#         except Booking.DoesNotExist:
#             return Response({
#                 "message": "Booking not found.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"booking_id": "Invalid or unauthorized booking"}
#             }, status=404)

#         return PaystackGateway.verify_payment(reference, booking)




#################### Hokidays and gamifications #################
####################################################################

# class HolidayView(APIView):
#     permission_classes = [IsAuthenticated]
#     @swagger_auto_schema(
#         operation_summary="Get all holidays",
#         operation_description="Retrieve all public holidays for the logged-in user's holiday calendar.",
#         responses={200: PublicHolidaySerializer(many=True)},
#     )
    
#     def get(self, request):
#         """Get all holidays for the user's calendar"""
#         user = request.user
#         calendar = user.holiday_calendar
#         if not calendar:
#             return Response({"error": "No holiday calendar set up"}, status=400)
            
#         holidays = PublicHoliday.objects.filter(calendar=calendar)
#         serializer = PublicHolidaySerializer(holidays, many=True)
#         return Response(serializer.data)
    
#     def post(self, request):
#         """Create a new holiday"""
#         user = request.user
#         calendar = user.holiday_calendar
#         if not calendar:
#             return Response({"error": "No holiday calendar set up"}, status=400)
            
#         serializer = PublicHolidaySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(calendar=calendar)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class HolidayDetailView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self, pk, user):
#         try:
#             calendar = user.holiday_calendar
#             if not calendar:
#                 return None
#             return PublicHoliday.objects.get(pk=pk, calendar=calendar)
#         except PublicHoliday.DoesNotExist:
#             return None
    
#     @holiday_detail_get
#     def get(self, request, pk):
#         """Get a specific holiday"""
#         holiday = self.get_object(pk, request.user)
#         if not holiday:
#             return Response({"error": "Holiday not found"}, status=404)
#         serializer = PublicHolidaySerializer(holiday)
#         return Response(serializer.data)
    
#     @holiday_detail_put
#     def put(self, request, pk):
#         """Update a specific holiday"""
#         holiday = self.get_object(pk, request.user)
#         if not holiday:
#             return Response({"error": "Holiday not found"}, status=404)
#         serializer = PublicHolidaySerializer(holiday, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     @holiday_detail_delete
#     def delete(self, request, pk):
#         """Delete a specific holiday"""
#         holiday = self.get_object(pk, request.user)
#         if not holiday:
#             return Response({"error": "Holiday not found"}, status=404)
#         holiday.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class UpcomingHolidaysView(APIView):
#     permission_classes = [IsAuthenticated]

#     @upcoming_holidays_get
#     def get(self, request):
#         """Get upcoming holidays for the user's country"""
#         user = request.user
#         calendar = user.holiday_calendar
#         if not calendar:
#             return Response({"error": "No holiday calendar set up"}, status=400)
            
#         today = date.today()
#         upcoming = PublicHoliday.objects.filter(
#             calendar=calendar,
#             date__gte=today
#         ).order_by('date')[:10]
        
#         serializer = PublicHolidaySerializer(upcoming, many=True)
#         return Response(serializer.data)

# class HolidayView(APIView):
#     """
#     Get all holidays for the logged-in user (current + next year).
#     Update user's holiday calendar country code.
#     """
#     permission_classes = [IsAuthenticated]

#     @holiday_detail_get
#     def get(self, request):
#         user = request.user
#         calendar = getattr(user, "holiday_calendar", None)

#         if not calendar or not calendar.is_enabled:
#             return error_response(
#                 message="No holiday calendar found",
#                 errors={"calendar": "No holiday calendar found"}
#             )

#         holidays = calendar.holidays.all().order_by("date")
#         serializer = PublicHolidaySerializer(holidays, many=True)

#         return success_response(
#             message="Fetched holidays successfully",
#             data=serializer.data
#         )

#     # @holiday_detail_post
#     def post(self, request):
#         """
#         Update the user's holiday calendar country code and sync holidays.
#         """
#         user = request.user
#         country_code = request.data.get("country_code")

#         if not country_code:
#             return error_response(
#                 message="Country code is required",
#                 errors={"country_code": "This field is required"},
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

    
#         calendar = user.get_calendar()

#         # Update country code + enable calendar
#         calendar.country_code = country_code
#         calendar.is_enabled = True
#         calendar.save(update_fields=["country_code", "is_enabled", "updated_at"])

#         # Queue the sync task
#         from .tasks import sync_user_holidays
#         task = sync_user_holidays.delay(user.id, country_code)

#         return success_response(
#             message="Holiday calendar updated successfully",
#             data={
#                 "country_code": country_code,
#                 "task_id": task.id,
#             },
#             status_code=status.HTTP_200_OK
#         )


# class UpcomingHolidaysView(APIView):
#     """
#     Get upcoming holidays for the logged-in user (today + future dates).
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user
#         calendar = user.get_calendar()

#         if not calendar.is_enabled:
#             return error_response(
#                 message="Holiday calendar is disabled",
#                 errors={"calendar": "Holiday calendar is disabled"}
#             )

#         today = now().date()
#         holidays = calendar.holidays.filter(date__gte=today).order_by("date")
#         serializer = PublicHolidaySerializer(holidays, many=True)

#         return success_response(
#             message="Fetched upcoming holidays successfully",
#             data=serializer.data
#         )

# LOGGING ENDPOINTS ###############################


# BREAK SUGGESTION ENDPOINTS ###############################

# class BreakSuggestionListCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         """Get all break suggestions for the current user"""
#         suggestions = BreakSuggestion.objects.filter(user=request.user)
#         serializer = BreakSuggestionSerializer(suggestions, many=True)
#         return success_response(
#             message="Break suggestions retrieved successfully",
#             data=serializer.data
#         )
    
#     def post(self, request):
#         """Generate a break suggestion based on user data"""
#         try:
#             user = request.user
            
#             # Get user's mood, preferences, schedule, leave balance, blackout dates, special dates
#             # This would typically come from various models
#             leave_balance = LeaveBalance.objects.filter(user=user).first()
#             if not leave_balance:
#                 return error_response(
#                     message="Cannot generate suggestion",
#                     errors={"leave_balance": "User has no leave balance set up"},
#                     status_code=status.HTTP_400_BAD_REQUEST
#                 )
                
#             # Check if user has enough leave balance
#             if leave_balance.anual_leave_balance <= 0:
#                 return error_response(
#                     message="Cannot generate suggestion",
#                     errors={"leave_balance": "User has no leave days remaining"},
#                     status_code=status.HTTP_400_BAD_REQUEST
#                 )
            
#             # Get user's break preferences
#             preferences = BreakPreferences.objects.filter(user=user).first()
            
#             # Get user's working pattern
#             working_pattern = WorkingPattern.objects.filter(user=user).first()
            
#             # Get blackout dates
#             blackout_dates = BlackoutDate.objects.filter(user=user)
            
#             # Get special dates
#             special_dates = SpecialDate.objects.filter(user=user)
            
#             # Get user's recent mood
#             recent_mood = Mood.objects.filter(user=user).order_by('-created_at').first()
            
#             # Generate a suggestion based on collected data
#             # This is a simplified algorithm - in a real system, this would be more sophisticated
#             today = timezone.now().date()
            
#             # Start with a date range in the next 30 days
#             start_date = today + timedelta(days=random.randint(7, 14))
#             end_date = start_date + timedelta(days=random.randint(1, 3))
            
#             # Avoid weekends if working pattern exists
#             if working_pattern:
#                 # Adjust to avoid weekends or non-working days based on pattern
#                 while start_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
#                     start_date += timedelta(days=1)
#                 while end_date.weekday() >= 5:
#                     end_date += timedelta(days=1)
            
#             # Avoid blackout dates
#             for blackout in blackout_dates:
#                 # Convert datetime to date if needed
#                 blackout_start = blackout.start_date.date() if isinstance(blackout.start_date, datetime) else blackout.start_date
#                 blackout_end = blackout.end_date.date() if isinstance(blackout.end_date, datetime) else blackout.end_date
                
#                 if (blackout_start <= start_date <= blackout_end) or \
#                    (blackout_start <= end_date <= blackout_end):
#                     # Move dates forward past the blackout period
#                     start_date = blackout_end + timedelta(days=1)
#                     end_date = start_date + timedelta(days=random.randint(1, 3))
            
#             # Prioritize special dates if any are coming up
#             for special in special_dates:
#                 # Convert datetime to date if needed
#                 special_date = special.date.date() if isinstance(special.date, datetime) else special.date
                
#                 # If special date is within next 30 days, suggest a break around it
#                 if today <= special_date <= today + timedelta(days=30):
#                     start_date = special_date - timedelta(days=1)
#                     end_date = special_date + timedelta(days=1)
#                     break
            
#             # Generate title and description based on data
#             title = "Suggested Break"
#             description = "We recommend taking a break to recharge."
#             reason = "Based on your schedule and preferences"
            
#             # Adjust based on mood if available
#             based_on_mood = False
#             if recent_mood:
#                 based_on_mood = True
#                 # Map mood_type to a numeric score since Mood model doesn't have mood_score
#                 mood_scores = {
#                     "happy": 8,
#                     "sad": 3,
#                     "angry": 2,
#                     "neutral": 5,
#                     "excited": 9,
#                     "anxious": 3
#                 }
#                 mood_score = mood_scores.get(recent_mood.mood_type, 5)  # Default to 5 if unknown
                
#                 if mood_score < 5:  # Now using our mapped score
#                     title = "Wellness Break"
#                     description = "Your recent mood indicates you could benefit from some time off."
#                     reason = "Based on your recent mood tracking"
            
#             # Create the suggestion
#             suggestion = BreakSuggestion.objects.create(
#                 user=user,
#                 title=title,
#                 description=description,
#                 start_date=start_date,
#                 end_date=end_date,
#                 reason=reason,
#                 priority=10 if based_on_mood else 5,  # Using numeric values for priority
#                 based_on_mood=based_on_mood,
#                 based_on_workload=True,
#                 based_on_preferences=preferences is not None,
#                 based_on_weather=False  # Would require weather API integration
#             )
            
#             serializer = BreakSuggestionSerializer(suggestion)
#             return success_response(
#                 message="Break suggestion generated successfully",
#                 data=serializer.data,
#                 status_code=status.HTTP_201_CREATED
#             )
            
#         except Exception as e:
#             return error_response(
#                 message="Failed to generate break suggestion",
#                 errors={"detail": str(e)},
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )


# class BreakPlanActionView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self, pk, user):
#         try:
#             return BreakPlan.objects.get(pk=pk, user=user)
#         except BreakPlan.DoesNotExist:
#             return None

#     @break_plan_action
#     def patch(self, request, pk):
#         try:
#             user = request.user
#             break_plan = self.get_object(pk, user)
            
#             # If not found in BreakPlan, check BreakSuggestion
#             if not break_plan:
#                 try:
#                     suggestion = BreakSuggestion.objects.get(pk=pk, user=user)
#                 except BreakSuggestion.DoesNotExist:
#                     return error_response(
#                         message="Break plan/suggestion not found",
#                         errors={"break_plan": "Break plan/suggestion not found or you don't have permission"},
#                         status_code=status.HTTP_404_NOT_FOUND
#                     )
                
#                 # Prevent duplicate addition if already accepted
#                 if suggestion.is_accepted:
#                     return error_response(
#                         message="This suggested break has already been accepted.",
#                         errors={"break_suggestion": "Already accepted and added to break plan."},
#                         status_code=status.HTTP_409_CONFLICT
#                     )
                
#                 # Validate the action
#                 serializer = BreakPlanActionSerializer(data=request.data, context={'break_plan': None})
#                 if not serializer.is_valid():
#                     return error_response(
#                         message="Invalid action",
#                         errors=serializer.errors,
#                         status_code=status.HTTP_400_BAD_REQUEST
#                     )
                
#                 action = serializer.validated_data['action']
#                 reason = serializer.validated_data.get('reason', '')

#                 # Only create BreakPlan if action is 'accept'
#                 if action == 'accept':
#                     exists = BreakPlan.objects.filter(
#                         user=user,
#                         startDate=datetime.combine(suggestion.start_date, time.min),
#                         endDate=datetime.combine(suggestion.end_date, time.max)
#                     ).exists()
#                     if exists:
#                         return error_response(
#                             message="Break plan already exists for these dates",
#                             errors={"break_plan": "Duplicate break plan"},
#                             status_code=status.HTTP_409_CONFLICT
#                         )
#                     # Create BreakPlan from suggestion
#                     break_plan = BreakPlan.objects.create(
#                         user=user,
#                         leave_balance=LeaveBalance.objects.filter(user=user).first(),
#                         startDate=datetime.combine(suggestion.start_date, time.min),
#                         endDate=datetime.combine(suggestion.end_date, time.max),
#                         description=suggestion.description,
#                         status='pending',
#                     )
#                     # Mark suggestion as accepted
#                     suggestion.is_accepted = True
#                     suggestion.save(update_fields=["is_accepted"])
#                     return success_response(
#                         message="Break plan created from suggestion",
#                         data=BreakPlanSerializer(break_plan).data,
#                         status_code=status.HTTP_201_CREATED
#                     )
#                 else:
#                     return error_response(
#                         message="Only 'accept' action is supported for suggestions",
#                         errors={"action": "Invalid action for suggestion"},
#                         status_code=status.HTTP_400_BAD_REQUEST
#                     )
            
#             # If found in BreakPlan, proceed as before
#             serializer = BreakPlanActionSerializer(data=request.data, context={'break_plan': break_plan})
#             if not serializer.is_valid():
#                 return error_response(
#                     message="Invalid action",
#                     errors=serializer.errors,
#                     status_code=status.HTTP_400_BAD_REQUEST
#                 )
            
#             action = serializer.validated_data['action']
#             reason = serializer.validated_data.get('reason', '')
            
#             action_to_status = {
#                 'approve': 'approved',
#                 'reject': 'rejected',
#                 'take': 'taken',
#                 'miss': 'missed',
#                 'cancel': 'cancelled'
#             }
            
#             if action in action_to_status:
#                 break_plan.status = action_to_status[action]
#                 if reason:
#                     break_plan.description = f"{break_plan.description}\n\nAction: {action}\nReason: {reason}"
#                 break_plan.save()
#                 return success_response(
#                     message=f"Break successfully {action_to_status[action]}",
#                     data=BreakPlanSerializer(break_plan).data
#                 )
#             else:
#                 return error_response(
#                     message="Invalid action",
#                     errors={"action": "Action not supported"},
#                     status_code=status.HTTP_400_BAD_REQUEST
#                 )
            
#         except Exception as e:
#             return error_response(
#                 message="Failed to update break plan",
#                 errors={"detail": str(e)},
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )

# class BreakLogListCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     @break_log_list
#     def get(self, request):
#         """Get all break logs for the current user"""
#         break_scores = BreakScore.objects.filter(user=request.user)
#         serializer = BreakScoreSerializer(break_scores, many=True)
#         return Response(serializer.data)
    
#     @break_log_create
#     def post(self, request):
#         """Log when a user takes a break"""
#         serializer = BreakScoreSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
        
       
#         break_score = serializer.save(user=request.user)
        
       
#         streak, created = StreakScore.objects.get_or_create(
#             user=request.user,
#             streak_period=request.data.get('streak_period', 'monthly')
#         )
#         streak.increment_streak(break_score.score_date)
#         streak.save()
        
       
#         user = request.user
#         user.total_break_score += break_score.score_value
#         if streak.longest_streak > user.highest_streak:
#             user.highest_streak = streak.longest_streak
#         user.save()
        
#         return Response(serializer.data, status=201)

# class BreakLogDetailView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self, pk):
#         try:
#             return BreakScore.objects.get(pk=pk, user=self.request.user)
#         except BreakScore.DoesNotExist:
#             raise Http404
    
#     @break_log_retrieve
#     def get(self, request, pk):
#         """Get a specific break log"""
#         break_score = self.get_object(pk)
#         serializer = BreakScoreSerializer(break_score)
#         return Response(serializer.data)
    
#     @break_log_update
#     def put(self, request, pk):
#         """Update a specific break log"""
#         break_score = self.get_object(pk)
#         serializer = BreakScoreSerializer(break_score, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
#     @break_log_delete
#     def delete(self, request, pk):
#         """Delete a specific break log"""
#         break_score = self.get_object(pk)
#         break_score.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



########### SCORE ENDPOINTS #####################
##############################################


# class ScoreSummaryView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     @score_summary
#     def get(self, request):
#         """Get user's current break score and streak information"""
#         user = request.user
        
#         # Get latest break scores
#         recent_breaks = BreakScore.objects.filter(user=user).order_by('-score_date')[:5]
#         break_serializer = BreakScoreSerializer(recent_breaks, many=True)
        
#         # Get streak information
#         streaks = StreakScore.objects.filter(user=user)
#         streak_serializer = StreakScoreSerializer(streaks, many=True)
        
#         # Get optimization score
#         optimization = OptimizationScore.objects.filter(user=user).order_by('-score_date').first()
#         optimization_serializer = OptimizationScoreSerializer(optimization) if optimization else None
        
#         return Response({
#             "total_break_score": user.total_break_score,
#             "highest_streak": user.highest_streak,
#             "recent_breaks": break_serializer.data,
#             "streaks": streak_serializer.data,
#             "optimization": optimization_serializer.data if optimization else None,
#         })



# ########STREAK BREAK ENDPOINT ###########################
# ############################################


# class StreakListCreateView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     @streak_list
#     def get(self, request):
#         """Get all streak scores for the current user"""
#         streaks = StreakScore.objects.filter(user=request.user)
#         serializer = StreakScoreSerializer(streaks, many=True)
#         return Response(serializer.data)
    
#     # @streak_create
#     # def post(self, request):
#     #     """Create a new streak score"""
#     #     serializer = StreakScoreSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save(user=request.user)
#     #     return Response(serializer.data, status=status.HTTP_201_CREATED)

# class StreakDetailView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self, pk):
#         try:
#             return StreakScore.objects.get(pk=pk, user=self.request.user)
#         except StreakScore.DoesNotExist:
#             raise Http404
    
#     @streak_retrieve
#     def get(self, request, pk):
#         """Get a specific streak score"""
#         streak = self.get_object(pk)
#         serializer = StreakScoreSerializer(streak)
#         return Response(serializer.data)
    
#     # @streak_update
#     # def put(self, request, pk):
#     #     """Update a specific streak score"""
#     #     streak = self.get_object(pk)
#     #     serializer = StreakScoreSerializer(streak, data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save()
#     #     return Response(serializer.data)
    
#     @streak_delete
#     def delete(self, request, pk):
#         """Delete a specific streak score"""
#         streak = self.get_object(pk)
#         streak.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)



# ########### BADGE ENDPOINT ############
# ###############################


# class BadgeListCreateView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     @badge_list
#     def get(self, request):
#         """Get all badges for the current user"""
#         badges = Badge.objects.filter(user=request.user)
#         serializer = BadgeSerializer(badges, many=True)
#         return Response(serializer.data)
    
#     # @badge_create
#     # def post(self, request):
#     #     """Create a new badge"""
#     #     serializer = BadgeSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save(user=request.user)
#     #     return Response(serializer.data, status=status.HTTP_201_CREATED)

# class BadgeDetailView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self, pk):
#         try:
#             return Badge.objects.get(pk=pk, user=self.request.user)
#         except Badge.DoesNotExist:
#             raise Http404
    
#     @badge_retrieve
#     def get(self, request, pk):
#         """Get a specific badge"""
#         badge = self.get_object(pk)
#         serializer = BadgeSerializer(badge)
#         return Response(serializer.data)
    
#     @badge_update
#     def put(self, request, pk):
#         """Update a specific badge"""
#         badge = self.get_object(pk)
#         serializer = BadgeSerializer(badge, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
#     @badge_delete
#     def delete(self, request, pk):
#         """Delete a specific badge"""
#         badge = self.get_object(pk)
#         badge.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class BadgeEligibilityView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     @badge_eligibility
#     def post(self, request):
#         """Check if user is eligible for new badges and award them"""
#         user = request.user
#         new_badges = []
        
#         # Check for Weekend Breaker badge
#         weekend_breaks = BreakScore.objects.filter(
#             user=user,
#             break_type='weekend',
#             score_date__gte=date.today() - timedelta(days=30)
#         ).count()
        
#         if weekend_breaks >= 8 and not Badge.objects.filter(user=user, badge_type='weekend_breaker', level='bronze').exists():
#             badge = Badge.objects.create(
#                 user=user,
#                 badge_type='weekend_breaker',
#                 level='bronze',
#                 description="Took breaks on 8 weekends in a month",
#                 requirements_met={"weekend_breaks": weekend_breaks}
#             )
#             new_badges.append(badge)
#             user.total_badges += 1
#             user.save()
        
#         # More checks still coming here...
        
#         serializer = BadgeSerializer(new_badges, many=True)
#         return Response(serializer.data)




# ############ OPTIMISATION ENDPINT ############
# ############################################ In core/views.py

# class OptimizationListCreateView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     @optimization_list
#     def get(self, request):
#         """Get all optimization scores for the current user"""
#         optimization_scores = OptimizationScore.objects.filter(user=request.user)
#         serializer = OptimizationScoreSerializer(optimization_scores, many=True)
#         return Response(serializer.data)
    
#     # @optimization_create
#     # def post(self, request):
#     #     """Create a new optimization score"""
#     #     serializer = OptimizationScoreSerializer(data=request.data)
#     #     serializer.is_valid(raise_exception=True)
#     #     serializer.save(user=request.user)
#     #     return Response(serializer.data, status=status.HTTP_201_CREATED)

# class OptimizationDetailView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self, pk):
#         try:
#             return OptimizationScore.objects.get(pk=pk, user=self.request.user)
#         except OptimizationScore.DoesNotExist:
#             raise Http404
    
#     @optimization_retrieve
#     def get(self, request, pk):
#         """Get a specific optimization score"""
#         optimization = self.get_object(pk)
#         serializer = OptimizationScoreSerializer(optimization)
#         return Response(serializer.data)
    
#     @optimization_update
#     def put(self, request, pk):
#         """Update a specific optimization score"""
#         optimization = self.get_object(pk)
#         serializer = OptimizationScoreSerializer(optimization, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
#     @optimization_delete
#     def delete(self, request, pk):
#         """Delete a specific optimization score"""
#         optimization = self.get_object(pk)
#         optimization.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class OptimizationCalculateView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     @optimization_calculate
#     def post(self, request):
#         """Calculate optimization score based on user's break patterns"""
#         user = request.user
        
#         # Get user's break preferences and working pattern
#         try:
#             preferences = BreakPreferences.objects.get(user=user)
#             pattern = WorkingPattern.objects.get(user=user)
#         except (BreakPreferences.DoesNotExist, WorkingPattern.DoesNotExist):
#             return Response({"error": "User preferences or working pattern not set"}, status=400)
        
#         # Calculate component scores based on user data
#         break_timing_score = self._calculate_timing_score(user, pattern, preferences)
#         break_frequency_score = self._calculate_frequency_score(user, preferences)
#         break_consistency_score = self._calculate_consistency_score(user)
        
#         # Create or update optimization score
#         score, created = OptimizationScore.objects.get_or_create(
#             user=user,
#             score_date=date.today(),
#             defaults={
#                 'break_timing_score': break_timing_score,
#                 'break_frequency_score': break_frequency_score,
#                 'break_consistency_score': break_consistency_score,
#                 'recommendations': self._generate_recommendations(break_timing_score, break_frequency_score, break_consistency_score)
#             }
#         )
        
#         if not created:
#             score.break_timing_score = break_timing_score
#             score.break_frequency_score = break_frequency_score
#             score.break_consistency_score = break_consistency_score
#             score.recommendations = self._generate_recommendations(break_timing_score, break_frequency_score, break_consistency_score)
#             score.save()
        
#         # Calculate total score
#         total_score = score.calculate_total_score()
#         score.save()
        
#         # Update user's last optimization score
#         user.last_optimization_score = total_score
#         user.save()
        
#         serializer = self.get_serializer(score)
#         return Response(serializer.data)
    
#     def _calculate_timing_score(self, user, pattern, preferences):
#         # Implementation of timing score calculation
#         pass
    
#     def _calculate_frequency_score(self, user, preferences):
#         # Implementation of frequency score calculation
#         pass
    
#     def _calculate_consistency_score(self, user):
#         # Implementation of consistency score calculation
#         pass
    
#     def _generate_recommendations(self, timing_score, frequency_score, consistency_score):
#         # Generate personalized recommendations
#         recommendations = []
        
#         if timing_score < 60:
#             recommendations.append("Try taking breaks at more optimal times during your work day")
        
#         if frequency_score < 60:
#             recommendations.append("Consider increasing your break frequency to match your preferences")
        
#         if consistency_score < 60:
#             recommendations.append("Work on maintaining a consistent break schedule")
        
#         return recommendations