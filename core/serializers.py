from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import (User, Client, DateEntry, BreakPlan, LeaveBalance, BreakPreferences, 
BreakPlan, LastLogin, UserSettings,
PublicHoliday, PasswordResetOTP, WorkingPattern, 
OptimizationGoal, UserNotificationPreference, Mood,
Event, Booking,
BlackoutDate,
SpecialDate
# OnboardingData,
# WellbeingQuestion,
# WellbeingScore,
# GamificationData,
)
from .validators import validate_password, validate_leave_balance, validate_preferences, validate_break_plan
from django.contrib.auth.hashers import make_password 
from django.contrib.auth import get_user_model
from core.utils import send_otp_email
import random
from datetime import datetime, date
from uuid import UUID
import pytz


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=False, allow_blank=True, help_text="Optional full name")

    class Meta:
        model = User
        fields = ["email", "full_name", "password", "password_confirmation"]
        extra_kwargs = {
            "email": {"required": True, "help_text": "Email address for registration"},
            "password": {"help_text": "Password (will be validated against Django's password rules)"},
            "password_confirmation": {"help_text": "Confirm password"},
        }

    def validate(self, data):
        if data["password"] != data["password_confirmation"]:
            raise serializers.ValidationError({"errors": ["Passwords do not match"]})
        validate_password(data["password"])
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirmation", None)
        return User.objects.create_user(
            email=validated_data["email"],
            full_name=validated_data.get("full_name"),
            password=validated_data["password"]
        )

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Accepts email and returns a token upon successful authentication.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data["email"]
        password = data["password"]

        # Find user by email
        user = User.objects.filter(email=email).first()

        # Verify credentials
        if user and user.check_password(password):
            return {"user": user}
        else:
            raise serializers.ValidationError({"errors": ["Login failed"]})
        

class LogoutSerializer(serializers.Serializer):
    # Expect the raw refresh token that the client received at login
    refresh = serializers.CharField(required=True)

    def validate_refresh(self, value):
        """
        Ensure the string is a well‑formed, not‑yet‑expired refresh token.
        `RefreshToken` throws `TokenError` on any problem (malformed,
        signature mismatch, expired, blacklisted, etc.).
        """
        try:
            RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError("Invalid or expired refresh token")
        return value



class GoogleLoginSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)


class TwitterLoginSerializer(serializers.Serializer):
    provider_id = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)


class AppleLoginSerializer(serializers.Serializer):
    provider_id = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    

# class UserSerializer(serializers.ModelSerializer):
#     """
#     Serializer for user profile data.
#     Returns user details for endpoints like /api/profile.
#     """
#     class Meta:
#         model = User
#         fields = [
#             "id",
#             "full_name",
#             "email",
#             "first_name",
#             "last_name",
#             "profile_picture_path",
#             "holiday_days",
#             "birthday",
#             "home_location_timezone",
#             "home_location_coordinates",
#             "working_days_per_week",
#         ]




class UserSerializer(serializers.ModelSerializer):
    holiday_days = serializers.IntegerField(required=False, min_value=0, max_value=365)
    working_days_per_week = serializers.IntegerField(required=False, min_value=0, max_value=7)

    class Meta:
        model = User
        fields = [
            "id",
            "full_name",
            "email",
            "profile_picture_path",
            "holiday_days",
            "birthday",
            "home_location_timezone",
            "home_location_coordinates",
            "working_days_per_week",
        ]


# Request password reset otp serializer ________//

class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]

        otp = str(random.randint(100000, 999999))

        PasswordResetOTP.objects.create(
            email=email,
            otp=otp,
            created_at=timezone.now(),
            is_verified=False
        )

        success, message = send_otp_email(email, otp)

        if not success:
            raise serializers.ValidationError({"email": message})

        return validated_data

# Verify Email OTP Serializer________________/

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            record = PasswordResetOTP.objects.filter(
                email=data["email"], otp=data["otp"], is_verified=False
            ).latest("created_at")
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired OTP")

        if record.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        self.instance = record
        return data

    def save(self):
        self.instance.is_verified = True
        self.instance.save()


# Reset Password Serializer___________________/

class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)

    def validate(self, data):
        try:
            otp_obj = PasswordResetOTP.objects.filter(
                email=data["email"], otp=data["otp"], is_verified=True
            ).latest("created_at")
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid or unverified OTP.")

        self.user = User.objects.get(email=data["email"])
        return data

    def save(self):
        self.user.password = make_password(self.validated_data["new_password"])
        self.user.save()


class DateEntrySerializer(serializers.ModelSerializer):
    # uuid = serializers.UUIDField(source="id")  # Include UUID in response
    optimisation_score = serializers.FloatField()

    class Meta:
        model = DateEntry
        fields = ["start_date", "end_date", "title", "description", "optimisation_score"]
        # fields = ["uuid", "start_date", "end_date", "title", "description", "optimisation_score"]



# class WellbeingScoreSerializer(serializers.ModelSerializer):
#     """
#     Serializer for wellbeing scores.
#     Validates score is between 0-10.
#     """
#     class Meta:
#         model = WellbeingScore
#         fields = "__all__"

#     def validate_score(self, value):
#         if not 0 <= value <= 10:
#             raise serializers.ValidationError("Score must be between 0 and 10")
#         return value

# class UpdateSettingsSerializer(serializers.ModelSerializer):
#     """
#     Serializer for updating user settings.
#     """
#     class Meta:
#         model = UserSettings
#         fields = ["settings_json"]

class ActionLogSerializer(serializers.Serializer):
    """
    Serializer for logging application actions.
    """
    application_area_name = serializers.CharField()
    action_description = serializers.CharField()
    action_duration_seconds = serializers.IntegerField()
    token = serializers.UUIDField(required=False)  # Optional user token

    def validate_action_duration_seconds(self, value):
        if value < 0:
            raise serializers.ValidationError("Duration cannot be negative")
        return value
    
# class OnboardingDataSerializer(serializers.ModelSerializer):
#     """
#     Serializer for onboarding data.
#     """
#     class Meta:
#         model = OnboardingData
#         fields = ["id", "survey_completion_date", "survey_results"]


class PublicHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicHoliday
        fields = ["id", "name", "date", "country_code"]


# class WellbeingQuestionSerializer(serializers.ModelSerializer):
#     """
#     Serializer for the WellbeingQuestion model.
#     """
#     class Meta:
#         model = WellbeingQuestion
#         fields = ["id", "question_text", "score_type"]

# class GamificationDataSerializer(serializers.ModelSerializer):
#     smart_planning_score = serializers.IntegerField(read_only=True)

#     class Meta:
#         model = GamificationData
#         fields = [
#             "points",
#             "streak_days",
#             "badges",
#             "smart_planning_score"
#         ]
#         read_only_fields = ["points", "streak_days", "badges", "smart_planning_score"]


# ------------BREAK PLAN SERIALIZZER--------------


class BreakPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakPlan
        fields = '__all__'
        read_only_fields = ["user", "leave_balance"]

    def create(self, validated_data):
        user = self.context['request'].user
        leave_balance, _ = LeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                "anual_leave_balance": 60,
                "anual_leave_refresh_date": date.today().replace(year=date.today().year + 1),
                "already_used_balance": 0,
            }
        )
        validated_data['user'] = user
        validated_data['leave_balance'] = leave_balance
        return super().create(validated_data)


        # -----------------

# ==========BREAK LIST SERIALIZERS===============
class BreakPlanListSerializer(serializers.ModelSerializer):
    daysCount = serializers.SerializerMethodField()
    daysRemaining = serializers.SerializerMethodField()

    class Meta:
        model = BreakPlan
        fields = [
            "id", "startDate", "endDate", "description", "type", "status",
            "daysCount", "daysRemaining", "created_at", "updated_at"
        ]

    def get_daysCount(self, obj):
        try:
            return (obj.endDate.date() - obj.startDate.date()).days + 1
        except Exception:
            return 0

    def get_daysRemaining(self, obj):
        try:
            today = date.today()
            return max((obj.endDate.date() - today).days, 0)
        except Exception:
            return 0


# ------------------

# ==========BREAK PLAN UPDATE SERIALIZERS===============
class BreakPlanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakPlan
        fields = ["startDate", "endDate", "description", "status"]

    def validate(self, data):
        return validate_break_plan(data)
    


# ==========BREAK LEAVE BALANCCE SERIALIZERS===============
class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = ['anual_leave_balance', 'anual_leave_refresh_date', 'already_used_balance']
        extra_kwargs = {
            'anual_leave_balance': {'required': True},
            'anual_leave_refresh_date': {'required': True},
            'already_used_balance': {'required': True}
        }

    def validate(self, data):
        return validate_leave_balance(data)


# ==========BREAK PREFERENCES SERIALIZERS===============
class BreakPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakPreferences
        fields = ['preference', 'weather_based_recommendation', 'to_be_confirmed']

    def validate(self, data):
        return validate_preferences(data)


from rest_framework import serializers

# ==========FIRST LOGIN SETUP SERIALIZERS===============

# class FirstLoginSetupSerializer(serializers.Serializer):
#     LeaveBalance = LeaveBalanceSerializer(required=True)
#     Preferences = BreakPreferencesSerializer(required=True)
#     BreakPlan = BreakPlanSerializer(required=False)

#     def validate(self, attrs):
#         """
#         Custom validation for the setup:
#         - Ensure BreakPlan has both startDate and endDate if provided.
#         """
#         break_plan = attrs.get("BreakPlan")
#         if break_plan:
#             if not break_plan.get("startDate") or not break_plan.get("endDate"):
#                 raise serializers.ValidationError({
#                     "BreakPlan": "Both startDate and endDate are required if BreakPlan is provided."
#                 })
#         return attrs


class FirstLoginSetupSerializer(serializers.Serializer):
    LeaveBalance = LeaveBalanceSerializer(required=True)
    BreakPreferences = BreakPreferencesSerializer(required=True)
    BreakPlan = BreakPlanSerializer(required=False)

    def validate(self, attrs):
        """
        Custom validation for setup:
        - Ensure BreakPlan has both startDate and endDate if provided.
        - Reject unexpected keys (like 'Preferences' instead of 'BreakPreferences').
        """
        # Get raw request data to compare keys
        incoming_keys = set(self.initial_data.keys())
        expected_keys = {"LeaveBalance", "BreakPreferences", "BreakPlan"}

        unexpected = incoming_keys - expected_keys
        if unexpected:
            raise serializers.ValidationError({
                "error": f"Unexpected field(s): {', '.join(unexpected)}. "
                         f"Expected only {', '.join(expected_keys)}"
            })

        # Validate BreakPlan dates
        break_plan = attrs.get("BreakPlan")
        if break_plan:
            if not break_plan.get("startDate") or not break_plan.get("endDate"):
                raise serializers.ValidationError({
                    "BreakPlan": "Both startDate and endDate are required if BreakPlan is provided."
                })

        return attrs
    
# GET and PUT action
class FirstLoginSetupDataSerializer(serializers.Serializer):
    LeaveBalance = LeaveBalanceSerializer()
    BreakPreferences = BreakPreferencesSerializer()
    BreakPlan = BreakPlanSerializer()



# ==========USER SETTINGS SERIALIZERS===============

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['theme', 'language', 'timezone', 'currency']

    def validate_theme(self, value):
        allowed = ['light', 'dark', 'system']
        if value not in allowed:
            raise serializers.ValidationError(f"Theme must be one of {allowed}")
        return value
    def validate_timezone(self, value):
        if value not in pytz.all_timezones:
            raise serializers.ValidationError("Invalid timezone")
        return value


# ======= USER NOTIFICATION SERILIZER ========

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationPreference
        fields = [
            'breaksReminder',
            'suggestions',
            'deadlineAlerts',
            'weeklyDigest',
            'pushEnabled',
            'emailEnabled'
        ]

# ======= USER-NOTIFICATION-SERILIZER ========
class WorkingPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingPattern
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

# ======= SPECIAL-DATE-SERILIZER ========
class SpecialDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialDate
        fields = ["id", "title", "date", "description", "created_at", "updated_at"]
        extra_kwargs = {
            "title": {"required": True},
            "date": {"required": True},
            "description": {"required": False},
        }

# ======= DECOY-BLACKOUT-DATE-LIST-SERILIZER ========
class BlackoutDateSerializer(serializers.ModelSerializer):
    """
    Serializer for blackout dates.
    """
    class Meta:
        model = BlackoutDate
        fields = "__all__"

# ======= BLACKOUT-DATE-LIST-SERILIZER ========
class BlackOutDateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        user = self.context['request'].user
        for item in validated_data:
            item['user'] = user
        return super().create(validated_data)

# ======= BLACKOUT-DATE-SERILIZER ========
class BlackOutDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackoutDate
        fields = '__all__'
        read_only_fields = ('user',)
        list_serializer_class = BlackOutDateListSerializer


# ======= OPTIMIZATION-GOAL-SERILIZER ========
class OptimizationGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizationGoal
        fields = '__all__'
        read_only_fields = ('user',)



# ======= Mood-SERILIZER ========
class MoodCheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ["mood_type", "note"]

class MoodHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ["mood_type", "note", "created_at"]


# ======= Weather-SERILIZER ========

class WeatherForecastDaySerializer(serializers.Serializer):
    time = serializers.CharField()
    values = serializers.DictField()



########################################
######Event and Booking Serializers######



class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "location",
            "start_date",
            "end_date",
            "price",
            "image",
            "created_at",
            "updated_at",
        ]


class BookingSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "event",
            "user",
            "is_paid",
            "created_at",
        ]
        read_only_fields = ["user", "is_paid", "created_at"]


class PaymentSerializer(serializers.Serializer):
    """
    Serializer for payment initiation and verification
    """
    booking_id = serializers.IntegerField(required=True)
    reference = serializers.CharField(read_only=True)
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    status = serializers.CharField(read_only=True)
    authorization_url = serializers.CharField(read_only=True)

###################################################