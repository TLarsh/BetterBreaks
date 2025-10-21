from rest_framework import serializers
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from core.models.user_models import PasswordResetOTP, User
import random
from core.utils.email_utils import send_otp_email 


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
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(min_length=8, write_only=True)

    def validate(self, data):
        # Check OTP validity
        try:
            otp_obj = PasswordResetOTP.objects.filter(
                email=data["email"], otp=data["otp"], is_verified=True
            ).latest("created_at")
        except PasswordResetOTP.DoesNotExist:
            raise serializers.ValidationError({"otp": "Invalid or unverified OTP."})

        # Check confirm password
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        # Validate password strength
        try:
            validate_password(data["new_password"])
        except ValueError as e:
            raise serializers.ValidationError({"new_password": str(e)})

        # Attach user for save()
        try:
            self.user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        return data

    def save(self):
        self.user.password = make_password(self.validated_data["new_password"])
        self.user.save()

######## CHANGE EMAIL and PASSWORD SERIALIZERS ##############

class ChangeEmailSerializer(serializers.Serializer):
    new_email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["password"]):
            raise serializers.ValidationError({"password": "Incorrect password."})

        if User.objects.filter(email=data["new_email"]).exclude(id=user.id).exists():
            raise serializers.ValidationError({"new_email": "This email is already taken."})

        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.email = self.validated_data["new_email"]
        user.save()
        return user

# -----------------------------------------------------------------

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user

        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError({"old_password": "Old password is incorrect."})

        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})

        
        try:
            validate_password(data["new_password"])
        except ValueError as e:
            raise serializers.ValidationError({"new_password": str(e)})

        return data

    def save(self, **kwargs):
        user = self.context["request"].user
        user.password = make_password(self.validated_data["new_password"])
        user.save()
        return user