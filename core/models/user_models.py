from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from .holiday_models import PublicHolidayCalendar


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, full_name=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        
        email = self.normalize_email(email)

        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, full_name=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, full_name=full_name, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_picture_path = models.CharField(max_length=255, null=True, blank=True)
    holiday_days = models.PositiveIntegerField(null=True, blank=True)
    birthday = models.DateTimeField(null=True, blank=True)
    home_location_timezone = models.CharField(max_length=100, null=True, blank=True)
    home_location_coordinates = models.CharField(max_length=255, null=True, blank=True)
    working_days_per_week = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    google_oauth_token = models.CharField(max_length=255, null=True, blank=True)
    
    # Gamification fields
    total_break_score = models.PositiveIntegerField(default=0)
    total_badges = models.PositiveIntegerField(default=0)
    highest_streak = models.PositiveIntegerField(default=0)
    last_optimization_score = models.FloatField(default=0.0)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email if not self.full_name else self.full_name
    
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return{
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

    def get_calendar(self):
        """
        Always return a holiday calendar for this user.
        If missing, create one with a default country code.
        """
        # from .models import PublicHolidayCalendar  # local import to avoid circulars

        calendar, _ = PublicHolidayCalendar.objects.get_or_create(
            user=self,
            defaults={"country_code": "US"}
        )
        return calendar

class SocialAccount(models.Model):
    PROVIDER_CHOICES = [
        ("google", "Google"),
        ("twitter", "Twitter"),
        ("apple", "Apple"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="social_accounts", on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_id = models.CharField(max_length=255, db_index=True)
    email = models.EmailField(blank=True, null=True)
    extra_data = models.JSONField(default=dict, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "provider_id")
        indexes = [models.Index(fields=["provider", "provider_id"])]

    def __str__(self):
        return f"{self.provider} | {self.user.email}"

    
# Clients Table

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_name = models.CharField(max_length=100, null=False, blank=False)
    client_description = models.TextField(null=False, blank=False)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.client_name
    
# Last Logis Table

class LastLogin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    client = models.ForeignKey("User", on_delete=models.CASCADE, related_name='login_event', related_query_name="login_event",)
    # token = models.UUIDField(default=uuid.uuid4, unique=True)
    token = models.CharField(max_length=512, unique=True)
    token_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.login_date}"


# Password Reset Table
class PasswordResetOTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)