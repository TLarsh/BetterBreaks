from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.timezone import now
from .models import (User, Client, DateEntry, BreakPlan, BreakSuggestion, LeaveBalance, BreakPreferences, 
BreakPlan, LastLogin, UserSettings,
PublicHoliday, PasswordResetOTP, WorkingPattern, 
OptimizationGoal, UserNotificationPreference, Mood,
Event, Booking,
BlackoutDate,
SpecialDate,
# Models moved from gamification_models.py
BreakScore, StreakScore, Badge, OptimizationScore
# OnboardingData,
# WellbeingQuestion,
# WellbeingScore,
# GamificationData,
)
from .utils.validator_utils import validate_password, validate_leave_balance, validate_preferences, validate_break_plan
from django.contrib.auth.hashers import make_password 
from django.contrib.auth import get_user_model
from core.utils import send_otp_email
import random
from datetime import datetime, date
from uuid import UUID
import pytz


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     password_confirmation = serializers.CharField(write_only=True)
#     full_name = serializers.CharField(required=False, allow_blank=True, help_text="Optional full name")

#     class Meta:
#         model = User
#         fields = ["email", "full_name", "password", "password_confirmation"]
#         extra_kwargs = {
#             "email": {"required": True, "help_text": "Email address for registration"},
#             "password": {"help_text": "Password (will be validated against Django's password rules)"},
#             "password_confirmation": {"help_text": "Confirm password"},
#         }

#     def validate(self, data):
#         if data["password"] != data["password_confirmation"]:
#             raise serializers.ValidationError({"errors": ["Passwords do not match"]})
#         validate_password(data["password"])
#         return data

#     def create(self, validated_data):
#         validated_data.pop("password_confirmation", None)
#         return User.objects.create_user(
#             email=validated_data["email"],
#             full_name=validated_data.get("full_name"),
#             password=validated_data["password"]
#         )

# class LoginSerializer(serializers.Serializer):
#     """
#     Serializer for user login.
#     Accepts email and returns a token upon successful authentication.
#     """
#     email = serializers.EmailField()
#     password = serializers.CharField()

#     def validate(self, data):
#         email = data["email"]
#         password = data["password"]

#         # Find user by email
#         user = User.objects.filter(email=email).first()

#         # Verify credentials
#         if user and user.check_password(password):
#             return {"user": user}
#         else:
#             raise serializers.ValidationError({"errors": ["Login failed"]})
        

# class LogoutSerializer(serializers.Serializer):
#     # Expect the raw refresh token that the client received at login
#     refresh = serializers.CharField(required=True)

#     def validate_refresh(self, value):
#         """
#         Ensure the string is a well‑formed, not‑yet‑expired refresh token.
#         `RefreshToken` throws `TokenError` on any problem (malformed,
#         signature mismatch, expired, blacklisted, etc.).
#         """
#         try:
#             RefreshToken(value)
#         except TokenError:
#             raise serializers.ValidationError("Invalid or expired refresh token")
#         return value



# class GoogleLoginSerializer(serializers.Serializer):
#     token = serializers.CharField(required=True)


# class TwitterLoginSerializer(serializers.Serializer):
#     provider_id = serializers.CharField(required=True)
#     email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)


# class AppleLoginSerializer(serializers.Serializer):
#     provider_id = serializers.CharField(required=True)
#     email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    

# # class UserSerializer(serializers.ModelSerializer):
# #     """
# #     Serializer for user profile data.
# #     Returns user details for endpoints like /api/profile.
# #     """
# #     class Meta:
# #         model = User
# #         fields = [
# #             "id",
# #             "full_name",
# #             "email",
# #             "first_name",
# #             "last_name",
# #             "profile_picture_path",
# #             "holiday_days",
# #             "birthday",
# #             "home_location_timezone",
# #             "home_location_coordinates",
# #             "working_days_per_week",
# #         ]




# class UserSerializer(serializers.ModelSerializer):
#     holiday_days = serializers.IntegerField(required=False, min_value=0, max_value=365)
#     working_days_per_week = serializers.IntegerField(required=False, min_value=0, max_value=7)

#     class Meta:
#         model = User
#         fields = [
#             "id",
#             "full_name",
#             "email",
#             "profile_picture_path",
#             "holiday_days",
#             "birthday",
#             "home_location_timezone",
#             "home_location_coordinates",
#             "working_days_per_week",
#         ]


# # Request password reset otp serializer ________//

# class RequestOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField()

#     def validate_email(self, value):
#         if not User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("No user found with this email.")
#         return value

#     def create(self, validated_data):
#         email = validated_data["email"]

#         otp = str(random.randint(100000, 999999))

#         PasswordResetOTP.objects.create(
#             email=email,
#             otp=otp,
#             created_at=timezone.now(),
#             is_verified=False
#         )

#         success, message = send_otp_email(email, otp)

#         if not success:
#             raise serializers.ValidationError({"email": message})

#         return validated_data

# # Verify Email OTP Serializer________________/

# class VerifyOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     otp = serializers.CharField(max_length=6)

#     def validate(self, data):
#         try:
#             record = PasswordResetOTP.objects.filter(
#                 email=data["email"], otp=data["otp"], is_verified=False
#             ).latest("created_at")
#         except PasswordResetOTP.DoesNotExist:
#             raise serializers.ValidationError("Invalid or expired OTP")

#         if record.is_expired():
#             raise serializers.ValidationError("OTP has expired.")

#         self.instance = record
#         return data

#     def save(self):
#         self.instance.is_verified = True
#         self.instance.save()


# # Reset Password Serializer___________________/

# class ResetPasswordSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     otp = serializers.CharField(max_length=6)
#     new_password = serializers.CharField(min_length=8, write_only=True)
#     confirm_password = serializers.CharField(min_length=8, write_only=True)

#     def validate(self, data):
#         # Check OTP validity
#         try:
#             otp_obj = PasswordResetOTP.objects.filter(
#                 email=data["email"], otp=data["otp"], is_verified=True
#             ).latest("created_at")
#         except PasswordResetOTP.DoesNotExist:
#             raise serializers.ValidationError({"otp": "Invalid or unverified OTP."})

#         # Check confirm password
#         if data["new_password"] != data["confirm_password"]:
#             raise serializers.ValidationError(
#                 {"confirm_password": "Passwords do not match."}
#             )

#         # Validate password strength
#         try:
#             validate_password(data["new_password"])
#         except ValueError as e:
#             raise serializers.ValidationError({"new_password": str(e)})

#         # Attach user for save()
#         try:
#             self.user = User.objects.get(email=data["email"])
#         except User.DoesNotExist:
#             raise serializers.ValidationError({"email": "User not found."})

#         return data

#     def save(self):
#         self.user.password = make_password(self.validated_data["new_password"])
#         self.user.save()

# ######## CHANGE EMAIL and PASSWORD SERIALIZERS ##############

# class ChangeEmailSerializer(serializers.Serializer):
#     new_email = serializers.EmailField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = self.context["request"].user
#         if not user.check_password(data["password"]):
#             raise serializers.ValidationError({"password": "Incorrect password."})

#         if User.objects.filter(email=data["new_email"]).exclude(id=user.id).exists():
#             raise serializers.ValidationError({"new_email": "This email is already taken."})

#         return data

#     def save(self, **kwargs):
#         user = self.context["request"].user
#         user.email = self.validated_data["new_email"]
#         user.save()
#         return user

# # -----------------------------------------------------------------

# class ChangePasswordSerializer(serializers.Serializer):
#     old_password = serializers.CharField(write_only=True)
#     new_password = serializers.CharField(write_only=True)
#     confirm_password = serializers.CharField(write_only=True)

#     def validate(self, data):
#         user = self.context["request"].user

#         if not user.check_password(data["old_password"]):
#             raise serializers.ValidationError({"old_password": "Old password is incorrect."})

#         if data["new_password"] != data["confirm_password"]:
#             raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        
#         try:
#             validate_password(data["new_password"])
#         except ValueError as e:
#             raise serializers.ValidationError({"new_password": str(e)})

#         return data

#     def save(self, **kwargs):
#         user = self.context["request"].user
#         user.password = make_password(self.validated_data["new_password"])
#         user.save()
#         return user
################################################################

####### CONTACT US #########
# from rest_framework import serializers
# from .models import ContactMessage

# class ContactMessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ContactMessage
#         fields = ["full_name", "email", "subject", "message"]

#     def validate_message(self, value):
#         if len(value.strip()) < 10:
#             raise serializers.ValidationError("Message must be at least 10 characters long.")
#         return value




# ######## DATE ENTRY ##########

# class DateEntrySerializer(serializers.ModelSerializer):
#     # uuid = serializers.UUIDField(source="id")  # Include UUID in response
#     optimisation_score = serializers.FloatField()

#     class Meta:
#         model = DateEntry
#         fields = ["start_date", "end_date", "title", "description", "optimisation_score"]
#         # fields = ["uuid", "start_date", "end_date", "title", "description", "optimisation_score"]



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

# class ActionLogSerializer(serializers.Serializer):
#     """
#     Serializer for logging application actions.
#     """
#     application_area_name = serializers.CharField()
#     action_description = serializers.CharField()
#     action_duration_seconds = serializers.IntegerField()
#     token = serializers.UUIDField(required=False)  # Optional user token

#     def validate_action_duration_seconds(self, value):
#         if value < 0:
#             raise serializers.ValidationError("Duration cannot be negative")
#         return value
    
# class OnboardingDataSerializer(serializers.ModelSerializer):
#     """
#     Serializer for onboarding data.
#     """
#     class Meta:
#         model = OnboardingData
#         fields = ["id", "survey_completion_date", "survey_results"]


# class PublicHolidaySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PublicHoliday
#         fields = ["id", "name", "date", "country_code"]


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


# class BreakPlanSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BreakPlan
#         fields = '__all__'
#         read_only_fields = ["user", "leave_balance"]

#     def create(self, validated_data):
#         user = self.context['request'].user
#         leave_balance, _ = LeaveBalance.objects.get_or_create(
#             user=user,
#             defaults={
#                 "anual_leave_balance": 60,
#                 "anual_leave_refresh_date": date.today().replace(year=date.today().year + 1),
#                 "already_used_balance": 0,
#             }
#         )
#         validated_data['user'] = user
#         validated_data['leave_balance'] = leave_balance
#         return super().create(validated_data)


        # -----------------


# # ==========BREAK LIST SERIALIZERS===============
# class BreakPlanListSerializer(serializers.ModelSerializer):
#     daysCount = serializers.SerializerMethodField()
#     daysRemaining = serializers.SerializerMethodField()

#     class Meta:
#         model = BreakPlan
#         fields = [
#             "id", "startDate", "endDate", "description", "type", "status",
#             "daysCount", "daysRemaining", "created_at", "updated_at"
#         ]

#     def get_daysCount(self, obj):
#         try:
#             return (obj.endDate.date() - obj.startDate.date()).days + 1
#         except Exception:
#             return 0

#     def get_daysRemaining(self, obj):
#         try:
#             today = date.today()
#             return max((obj.endDate.date() - today).days, 0)
#         except Exception:
#             return 0


# # ------------------

# class UpcomingBreakPlanSerializer(serializers.ModelSerializer):
#     days = serializers.SerializerMethodField()
#     status_display = serializers.CharField(source="get_status_display", read_only=True)
#     starts_in = serializers.SerializerMethodField()
#     local_start_date = serializers.SerializerMethodField()

#     class Meta:
#         model = BreakPlan
#         fields = [
#             "id",
#             "description",
#             "type",
#             "status",
#             "status_display",
#             "startDate",
#             "endDate",
#             "days",
#             "starts_in",
#             "local_start_date",
#         ]

#     def get_days(self, obj):
#         return (obj.endDate.date() - obj.startDate.date()).days + 1

#     def get_starts_in(self, obj):
#         today = now().date()
#         diff = (obj.startDate.date() - today).days
#         return f"In {diff} days" if diff >= 0 else "Started already"

#     def get_local_start_date(self, obj):
#         user = obj.user
#         if not user.home_location_timezone:
#             return obj.startDate.date()

#         try:
#             tz = pytz.timezone(user.home_location_timezone)
#             local_dt = obj.startDate.astimezone(tz)
#             return local_dt.strftime("%B %d")  # Example: "April 24"
#         except Exception:
#             return obj.startDate.date()


# # ==========BREAK SUGGESTION SERIALIZERS===============
# class BreakSuggestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BreakSuggestion
#         fields = ['id', 'title', 'description', 'start_date', 'end_date', 'reason', 'priority',
#                  'is_accepted', 'based_on_mood', 'based_on_workload', 'based_on_preferences',
#                  'based_on_weather', 'created_at']
#         read_only_fields = ['id', 'created_at']

# # ==========BREAK PLAN UPDATE SERIALIZERS===============
# class BreakPlanUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BreakPlan
#         fields = ["startDate", "endDate", "description", "status"]

#     def validate(self, data):
#         return validate_break_plan(data)

# class BreakPlanActionSerializer(serializers.Serializer):
#     action = serializers.ChoiceField(choices=['approve', 'reject', 'take', 'miss', 'cancel', 'accept'])
#     reason = serializers.CharField(required=False, allow_blank=True)
    
#     def validate_action(self, value):
#         break_plan = self.context.get('break_plan')
#         # If break_plan is None, it's a suggestion, allow only 'accept'
#         if not break_plan:
#             if value != 'accept':
#                 raise serializers.ValidationError("Only 'accept' action is allowed for suggestions.")
#             return value

#         current_status = break_plan.status
#         valid_transitions = {
#             'planned': ['approve', 'reject', 'cancel'],
#             'pending': ['approve', 'reject', 'cancel'],
#             'approved': ['take', 'miss', 'cancel'],
#             'rejected': [],
#             'taken': [],
#             'missed': [],
#             'cancelled': [],
#         }
#         if value not in valid_transitions.get(current_status, []):
#             raise serializers.ValidationError(
#                 f"Cannot perform '{value}' action on a break with '{current_status}' status"
#             )
#         return value


# # ==========BREAK LEAVE BALANCCE SERIALIZERS===============
# class LeaveBalanceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = LeaveBalance
#         fields = ['anual_leave_balance', 'anual_leave_refresh_date', 'already_used_balance']
#         extra_kwargs = {
#             'anual_leave_balance': {'required': True},
#             'anual_leave_refresh_date': {'required': True},
#             'already_used_balance': {'required': True}
#         }

#     def validate(self, data):
#         return validate_leave_balance(data)


# # ==========BREAK PREFERENCES SERIALIZERS===============
# class BreakPreferencesSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BreakPreferences
#         fields = ['preference', 'weather_based_recommendation', 'to_be_confirmed']

#     def validate(self, data):
#         return validate_preferences(data)


# from rest_framework import serializers

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


# class FirstLoginSetupSerializer(serializers.Serializer):
#     LeaveBalance = LeaveBalanceSerializer(required=True)
#     BreakPreferences = BreakPreferencesSerializer(required=True)
#     BreakPlan = BreakPlanSerializer(required=False)

#     def validate(self, attrs):
#         """
#         Custom validation for setup:
#         - Ensure BreakPlan has both startDate and endDate if provided.
#         - Reject unexpected keys (like 'Preferences' instead of 'BreakPreferences').
#         """
#         # Get raw request data to compare keys
#         incoming_keys = set(self.initial_data.keys())
#         expected_keys = {"LeaveBalance", "BreakPreferences", "BreakPlan"}

#         unexpected = incoming_keys - expected_keys
#         if unexpected:
#             raise serializers.ValidationError({
#                 "error": f"Unexpected field(s): {', '.join(unexpected)}. "
#                          f"Expected only {', '.join(expected_keys)}"
#             })

#         # Validate BreakPlan dates
#         break_plan = attrs.get("BreakPlan")
#         if break_plan:
#             if not break_plan.get("startDate") or not break_plan.get("endDate"):
#                 raise serializers.ValidationError({
#                     "BreakPlan": "Both startDate and endDate are required if BreakPlan is provided."
#                 })

#         return attrs
    
# # GET and PUT action
# class FirstLoginSetupDataSerializer(serializers.Serializer):
#     LeaveBalance = LeaveBalanceSerializer()
#     BreakPreferences = BreakPreferencesSerializer()
#     BreakPlan = BreakPlanSerializer()



# # ==========USER SETTINGS SERIALIZERS===============

# class UserSettingsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserSettings
#         fields = ['theme', 'language', 'timezone', 'currency']

#     def validate_theme(self, value):
#         allowed = ['light', 'dark', 'system']
#         if value not in allowed:
#             raise serializers.ValidationError(f"Theme must be one of {allowed}")
#         return value
#     def validate_timezone(self, value):
#         if value not in pytz.all_timezones:
#             raise serializers.ValidationError("Invalid timezone")
#         return value


# # ======= USER NOTIFICATION SERILIZER ========

# class NotificationPreferenceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserNotificationPreference
#         fields = [
#             'breaksReminder',
#             'suggestions',
#             'deadlineAlerts',
#             'weeklyDigest',
#             'pushEnabled',
#             'emailEnabled'
#         ]

# ======= WORKING PATTTERN-SERILIZER ========
# class WorkingPatternSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WorkingPattern
#         fields = '__all__'
#         read_only_fields = ['user', 'created_at']

# # ======= SPECIAL-DATE-SERILIZER ========
# class SpecialDateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SpecialDate
#         fields = ["id", "title", "date", "description", "created_at", "updated_at"]
#         extra_kwargs = {
#             "title": {"required": True},
#             "date": {"required": True},
#             "description": {"required": False},
#         }

# # ======= DECOY-BLACKOUT-DATE-LIST-SERILIZER ========
# class BlackoutDateSerializer(serializers.ModelSerializer):
#     """
#     Serializer for blackout dates.
#     """
#     class Meta:
#         model = BlackoutDate
#         fields = "__all__"

# # ======= BLACKOUT-DATE-LIST-SERILIZER ========
# class BlackOutDateListSerializer(serializers.ListSerializer):
#     def create(self, validated_data):
#         user = self.context['request'].user
#         for item in validated_data:
#             item['user'] = user
#         return super().create(validated_data)

# # ======= BLACKOUT-DATE-SERILIZER ========
# class BlackOutDateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BlackoutDate
#         fields = '__all__'
#         read_only_fields = ('user',)
#         list_serializer_class = BlackOutDateListSerializer


# ======= OPTIMIZATION-GOAL-SERILIZER ========
# class OptimizationGoalSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OptimizationGoal
#         fields = '__all__'
#         read_only_fields = ('user',)



# # ======= Mood-SERILIZER ========
# class MoodCheckInSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Mood
#         fields = ["mood_type", "note"]

# class MoodHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Mood
#         fields = ["mood_type", "note", "created_at"]


# ======= Weather-SERILIZER ========

# class WeatherForecastDaySerializer(serializers.Serializer):
#     time = serializers.CharField()
#     values = serializers.DictField()



########################################
######Event and Booking Serializers######



# class EventSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Event
#         fields = [
#             "id",
#             "title",
#             "description",
#             "location",
#             "start_date",
#             "end_date",
#             "price",
#             "image",
#             "created_at",
#             "updated_at",
#         ]


# class BookingSerializer(serializers.ModelSerializer):
#     event = EventSerializer(read_only=True)

#     class Meta:
#         model = Booking
#         fields = [
#             "id",
#             "event",
#             "user",
#             "is_paid",
#             "created_at",
#         ]
#         read_only_fields = ["user", "is_paid", "created_at"]


# class PaymentSerializer(serializers.Serializer):
#     """
#     Serializer for payment initiation and verification
#     """
#     booking_id = serializers.IntegerField(required=True)
#     reference = serializers.CharField(read_only=True)
#     amount = serializers.DecimalField(
#         max_digits=10, decimal_places=2, read_only=True
#     )
#     status = serializers.CharField(read_only=True)
#     authorization_url = serializers.CharField(read_only=True)

###################################################


# Gamification Serializers

# class BreakScoreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BreakScore
#         fields = ['id', 'score_date', 'score_value', 'frequency_points', 'adherence_points',
#                  'wellbeing_impact', 'break_type', 'notes', 'created_at', 'updated_at']
#         read_only_fields = ['user', 'created_at', 'updated_at']

# class StreakScoreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StreakScore
#         fields = ['id', 'current_streak', 'longest_streak', 'streak_period', 
#                  'last_break_date', 'streak_start_date', 'created_at', 'updated_at']
#         read_only_fields = ['user', 'created_at', 'updated_at']

# class BadgeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Badge
#         fields = ['id', 'badge_type', 'description', 'requirements_met', 
#                  'earned_date', 'created_at', 'updated_at']
#         read_only_fields = ['user', 'created_at', 'updated_at']

# class OptimizationScoreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = OptimizationScore
#         fields = ['id', 'score_date', 'score_value', 'break_timing_score', 
#                  'break_frequency_score', 'break_consistency_score', 
#                  'notes', 'recommendations', 'created_at', 'updated_at']
#         read_only_fields = ['user', 'created_at', 'updated_at']




