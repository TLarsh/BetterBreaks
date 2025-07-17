from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from django.db.models import Avg
from datetime import timedelta
import random
from django.utils import timezone
from django.utils.timezone import now
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    RequestOTPSerializer,
    VerifyOTPSerializer,
    ResetPasswordSerializer,
    UserSerializer,
    DateEntrySerializer,
    BlackoutDateSerializer,
    WellbeingScoreSerializer,
    UpdateSettingsSerializer,
    ActionLogSerializer,
    OnboardingDataSerializer,
    PublicHolidaySerializer,
    WellbeingQuestionSerializer,
    GamificationDataSerializer,
)
from .models import (
    LastLogin,
    UserSettings,
    DateEntry,
    BlackoutDate,
    WellbeingScore,
    ActionData,
    Client,
    OnboardingData,
    PublicHoliday,
    GamificationData,
    WellbeingQuestion,

)
import uuid
from .utils import create_calendar_event, fetch_public_holidays,calculate_smart_planning_score,award_badges,generate_holiday_suggestions,fetch_weather_data,adjust_score_based_on_weather, success_response, error_response
from drf_yasg.utils import swagger_auto_schema

User = get_user_model()  # Ensure your custom user model is properly configured


class RegisterView(APIView):
    """Handle user registration with password validation."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RegisterSerializer)
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return success_response(
                message="Registration successful",
                data={
                    "email": user.email,
                    "username": user.username
                },
                status_code=status.HTTP_201_CREATED
            )

        return error_response(
            message="Registration failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
)
class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LoginSerializer)
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

            return success_response(
                message="Login successful",
                data={
                    "refresh": tokens["refresh"],
                    "access": tokens["access"],
                    "email": user.email,
                    "username": user.username,
                }
            )

        return error_response(
            message="Login failed",
            errors=serializer.errors
        )
        

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
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )        


class RequestOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=RequestOTPSerializer)
    def post(self, request):
        serializer = RequestOTPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="OTP sent to your email.",
                data=None,
                status_code=status.HTTP_200_OK
            )
        return error_response(
            message="Failed to send OTP",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
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
class DateListView(APIView):
    """Retrieve authenticated user's dates."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        dates = DateEntry.objects.filter(user=request.user)
        serializer = DateEntrySerializer(dates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class BookEventView(APIView):
    @swagger_auto_schema(request_body=DateEntrySerializer)
    def post(self, request, date_entry_id):
        try:
            date_entry = DateEntry.objects.get(id=date_entry_id, user=request.user)
            create_calendar_event(request.user, date_entry)
            return Response({"success": True}, status=status.HTTP_200_OK)
        except DateEntry.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
        
class LogoutView(APIView):
    """Handle user logout by blacklisting the refresh token."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=LogoutSerializer)
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"errors": ["Refresh token is required"]},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
        
            token_obj = RefreshToken(refresh_token)

            
            jti = token_obj["jti"]
            LastLogin.objects.filter(token=jti).update(token_valid=False)

            
            token_obj.blacklist()

            return Response(status=status.HTTP_200_OK)

        except TokenError as e:
            return Response(
                {"errors": [str(e)]},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"errors": ["Server error"]},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class FetchPublicHolidaysView(APIView):
    def get(self, request):
        user = request.user
        if not user.home_location_timezone:
            return Response({"error": "User location not set"}, status=status.HTTP_400_BAD_REQUEST)

        country_code = user.home_location_timezone.split("/")[0]  # Extract country code
        year = timezone.now().year
        holidays_data = fetch_public_holidays(country_code, year)

        for holiday in holidays_data:
            PublicHoliday.objects.update_or_create(
                user=user,
                date=holiday["date"],
                defaults={"name": holiday["name"], "country_code": country_code}
            )

        return Response({"success": True}, status=status.HTTP_200_OK)
    

class ListPublicHolidaysView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        holidays = PublicHoliday.objects.filter(user=request.user)
        serializer = PublicHolidaySerializer(holidays, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BlackoutDatesView(APIView):
    """Retrieve authenticated user's blackout dates."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        blackout_dates = BlackoutDate.objects.filter(user=request.user)
        serializer = BlackoutDateSerializer(blackout_dates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ProfileView(APIView):
    """Retrieve user profile details."""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateWellbeingView(APIView):
    """Log user's wellbeing score."""
    @swagger_auto_schema(request_body=WellbeingScoreSerializer)
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        score = request.data.get("score")
        if not score:
            return Response(
                {"errors": ["Score is required"]}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            score = int(score)
            if not 0 <= score <= 10:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"errors": ["Score must be an integer between 0-10"]}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        WellbeingScore.objects.create(
            user=request.user,
            score=score,
            score_date=timezone.now()
        )
        return Response(status=status.HTTP_200_OK)

class LogActionView(APIView):
    """Log application actions (authenticated or unauthenticated)."""
    permission_classes = [AllowAny]  # Allow both authenticated and unauthenticated access

    @swagger_auto_schema(request_body=ActionLogSerializer)
    def post(self, request):
        serializer = ActionLogSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user = None
            token = data.get("token")
            if token:
                try:
                    # Ensure token is a string before converting to UUID
                    token_str = str(token)
                    token_uuid = uuid.UUID(token_str)
                    login_entry = LastLogin.objects.get(
                        token=token_uuid, token_valid=True
                    )
                    user = login_entry.user
                except (ValueError, LastLogin.DoesNotExist):
                    pass

            # Create the action log entry
            ActionData.objects.create(
                user=user,
                action_date=timezone.now(),
                ip_address=request.META.get("REMOTE_ADDR", ""),
                application_area_name=data["application_area_name"],
                action_description=data["action_description"],
                action_duration_seconds=data["action_duration_seconds"]
            )

            # If the user is authenticated, update gamification data
            if user:
                gamification_data, created = GamificationData.objects.get_or_create(user=user)

                # Award points for logging an action
                gamification_data.points += 10  # Example: 10 points per logged action
                gamification_data.save()

                # Update streak if the action is related to taking breaks
                if "break" in data["application_area_name"].lower():
                    last_break = DateEntry.objects.filter(
                        user=user, start_date__gte=timezone.now() - timezone.timedelta(days=1)
                    ).order_by("-start_date").first()

                    if last_break:
                        gamification_data.streak_days += 1
                    else:
                        gamification_data.streak_days = 1  # Reset streak if no recent breaks
                    gamification_data.save()

                # Award badges based on updated gamification data
                award_badges(user)

            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateProfileView(APIView):
    """Update user profile details."""
    @swagger_auto_schema(request_body=UserSerializer)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        user = request.user
        data = request.data
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.username = data.get("username", user.username)
        new_password = data.get("password")
        if new_password:
            try:
                from .validators import validate_password
                validate_password(new_password)
                user.set_password(new_password)
            except ValueError as e:
                return Response(
                    {"errors": [str(e)]}, status=status.HTTP_400_BAD_REQUEST
                )
        user.email = data.get("email", user.email)
        user.holiday_days = data.get("holiday_days", user.holiday_days)
        user.birthday = data.get("birthday", user.birthday)
        user.home_location_timezone = data.get(
            "home_location_timezone", user.home_location_timezone
        )
        user.home_location_coordinates = data.get(
            "home_location_coordinates", user.home_location_coordinates
        )
        user.working_days_per_week = data.get(
            "working_days_per_week", user.working_days_per_week
        )
        user.save()
        return Response({"success": True}, status=status.HTTP_200_OK)

class UpdateSettingsView(APIView):
    """Update user settings JSON."""
    @swagger_auto_schema(request_body=UpdateSettingsSerializer)
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        settings_json = request.data.get("settings_json")
        if not settings_json:
            return Response(
                {"errors": ["Settings JSON is required"]}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        # Ensure a default value is provided for settings_json
        user_settings, created = UserSettings.objects.get_or_create(
            user=request.user,
            defaults={"settings_json": {}},  # Default empty JSON object
        )
        user_settings.settings_json = settings_json
        user_settings.save()
        return Response(status=status.HTTP_200_OK)

class GetSettingsView(APIView):
    """Retrieve user settings JSON."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            settings = UserSettings.objects.get(user=request.user)
            return Response(
                {"settings_json": settings.settings_json}, 
                status=status.HTTP_200_OK
            )
        except UserSettings.DoesNotExist:
            return Response(
                {"settings_json": None}, status=status.HTTP_200_OK
            )
        
class GetOnboardingDataView(APIView):
    """Retrieve user's onboarding data."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            onboarding_data = OnboardingData.objects.get(user=request.user)
            serializer = OnboardingDataSerializer(onboarding_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OnboardingData.DoesNotExist:
            return Response(
                {"detail": "Onboarding data not found"}, status=status.HTTP_404_NOT_FOUND
            )


class UpdateOnboardingDataView(APIView):
    """Update or create user's onboarding data."""
    @swagger_auto_schema(request_body=OnboardingDataSerializer)
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        survey_results = request.data.get("survey_results")
        if not survey_results:
            return Response(
                {"errors": ["Survey results are required"]}, status=status.HTTP_400_BAD_REQUEST
            )
        # Update or create the onboarding data
        onboarding_data, created = OnboardingData.objects.update_or_create(
            user=request.user,
            defaults={"survey_results": survey_results},
        )
        serializer = OnboardingDataSerializer(onboarding_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class OptimizationScoreView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Step 1: Calculate the average wellbeing score over the last 7 days
        recent_scores = WellbeingScore.objects.filter(
            user=request.user,
            score_date__gte=timezone.now() - timedelta(days=7)
        ).aggregate(avg_score=Avg("score"))
        avg_wellbeing_score = recent_scores["avg_score"] or 0  # Default to 0 if no scores exist

        # Step 2: Count upcoming events in the next 30 days
        upcoming_events_count = DateEntry.objects.filter(
            user=request.user,
            start_date__gte=timezone.now(),
            start_date__lte=timezone.now() + timedelta(days=30)
        ).count()

        # Step 3: Check for blackout dates in the next 30 days
        blackout_dates = BlackoutDate.objects.filter(
            user=request.user,
            start_date__gte=timezone.now(),
            start_date__lte=timezone.now() + timedelta(days=30)
        )

        # Step 4: Fetch public holidays in the next 30 days
        public_holidays = PublicHoliday.objects.filter(
            user=request.user,
            date__gte=timezone.now().date(),
            date__lte=(timezone.now() + timedelta(days=30)).date()
        )

        # Step 5: Calculate the optimization score
        event_load_penalty = upcoming_events_count * 0.5  # Penalize for too many events
        public_holiday_bonus = len(public_holidays) * 2  # Bonus for public holidays
        optimization_score = avg_wellbeing_score - event_load_penalty + public_holiday_bonus

        # Step 6: Return the result
        return Response(
            {
                "optimization_score": round(optimization_score, 2),
                "details": {
                    "average_wellbeing_score": avg_wellbeing_score,
                    "upcoming_events_count": upcoming_events_count,
                    "public_holidays_count": len(public_holidays),
                    "blackout_dates": [
                        {"start_date": bd.start_date, "end_date": bd.end_date}
                        for bd in blackout_dates
                    ],
                },
            },
            status=status.HTTP_200_OK,
        )
    
class GamificationDataView(APIView):
    """Retrieve gamification data for the authenticated user."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        # Get or create gamification data
        gamification_data, created = GamificationData.objects.get_or_create(user=request.user)

        # Calculate the Smart Planning Score
        smart_planning_score = calculate_smart_planning_score(request.user)

        return Response(
            {
                "points": gamification_data.points,
                "streak_days": gamification_data.streak_days,
                "badges": gamification_data.badges,
                "smart_planning_score": smart_planning_score,
            },
            status=status.HTTP_200_OK,
        )
    

class UpdateWellbeingView(APIView):
    """Log user's wellbeing score and update gamification data."""
    @swagger_auto_schema(request_body=WellbeingScoreSerializer)
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        score = request.data.get("score")
        score_type = request.data.get("score_type")
        if not score or not score_type:
            return Response({"errors": ["Score and Score Type are required"]}, status=status.HTTP_400_BAD_REQUEST)

        WellbeingScore.objects.create(
            user=request.user,
            score=score,
            score_type=score_type,
            score_date=timezone.now()
        )
        

        # Update gamification data
        gamification_data, created = GamificationData.objects.get_or_create(user=request.user)
        gamification_data.points += 20  # Award 20 points for logging a wellbeing score
        gamification_data.save()

        # Award badges
        award_badges(request.user)

        return Response(status=status.HTTP_200_OK)
 
class SuggestedDatesView(APIView):
    """Generate suggested holidays and incorporate weather data."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Step 1: Generate holiday suggestions using BetterBreaksAI
        holiday_suggestions = generate_holiday_suggestions(request.user)

        # Step 2: Fetch user's coordinates
        if request.user.home_location_coordinates:
            try:
                latitude, longitude = request.user.home_location_coordinates.split(",")
                latitude = float(latitude.strip())
                longitude = float(longitude.strip())

                # Step 3: Adjust scores based on weather data
                for suggestion in holiday_suggestions:
                    start_date = suggestion["start_date"].date()  # Extract date from datetime
                    try:
                        weather_data = fetch_weather_data(latitude, longitude, start_date)
                        suggestion["score"] = adjust_score_based_on_weather(suggestion["score"], weather_data)
                    except Exception as e:
                        # Optionally log or ignore errors fetching weather
                        pass
            except Exception as e:
                # Handle invalid home_location_coordinates format gracefully
                pass  # Skip weather adjustment

        # Step 4: Return the final list of suggestions
        return Response(
            {
                "suggestions": [
                    {
                        "start_date": s["start_date"].isoformat(),
                        "end_date": s["end_date"].isoformat(),
                        "title": s["title"],
                        "description": s["description"],
                        "score": s["score"],
                    }
                    for s in holiday_suggestions
                ]
            },
            status=status.HTTP_200_OK,
        )
    

class AddDateView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = DateEntrySerializer(data=request.data)
        if serializer.is_valid():
            date_entry = serializer.save(user=request.user)
            return Response({"uuid": date_entry.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class DeleteDateView(APIView):
    def delete(self, request, date_uuid):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            date_entry = DateEntry.objects.get(id=date_uuid, user=request.user)
            date_entry.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except DateEntry.DoesNotExist:
            return Response({"error": "Date not found"}, status=status.HTTP_404_NOT_FOUND)
        



class WellbeingQuestionView(APIView):
    def get(self, request):
        questions = WellbeingQuestion.objects.all()
        serializer = WellbeingQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AddBlackoutDateView(APIView):
    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = BlackoutDateSerializer(data=request.data)
        if serializer.is_valid():
            blackout_date = serializer.save(user=request.user)
            return Response({"uuid": blackout_date.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeleteBlackoutDateView(APIView):
    def delete(self, request, blackout_uuid):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            blackout_date = BlackoutDate.objects.get(id=blackout_uuid, user=request.user)
            blackout_date.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except BlackoutDate.DoesNotExist:
            return Response({"error": "Blackout date not found"}, status=status.HTTP_404_NOT_FOUND)
