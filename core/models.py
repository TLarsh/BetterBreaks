from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import date, timedelta
from django.utils.text import slugify
import uuid

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
    date_joined = models.DateTimeField(auto_now_add=True)  # Added this field.
    google_oauth_token = models.CharField(max_length=255, null=True, blank=True)  # Addede this field

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

class SocialAccount(models.Model):
    PROVIDER_CHOICES = [
        ("google", "Google"),
        ("twitter", "Twitter"),
        ("apple", "Apple"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name="social_accounts", on_delete=models.CASCADE)
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_id = models.CharField(max_length=255, db_index=True)  # unique ID from provider
    email = models.EmailField(blank=True, null=True)
    extra_data = models.JSONField(default=dict, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)  # track last login from this provider
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("provider", "provider_id")
        indexes = [models.Index(fields=["provider", "provider_id"])]

    def __str__(self):
        return f"{self.provider} | {self.user.email}"

# User Settings Table

class UserSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    theme = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark'), ('system', 'System')], default='system')
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    currency = models.CharField(max_length=10, default='USD')

    def __str__(self):
        return f"{self.user.email}'s settings"

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     settings_json = models.JSONField(null=False, blank=False)

#     def __str__(self):
#         return f"Settings for {self.user.username}"
    
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
    
# Dates Table 
class DateEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=False, blank=False)
    end_date = models.DateTimeField(null=True, blank=True)
    recurring_event_expression = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(null=False, blank=False)
    event_status = models.CharField(
        max_length=20,
        choices=[("booked", "Booked"), ("pending", "Pending")],
        default="pending"
    )
    calendar_event_id = models.CharField(max_length=255, null=True, blank=True)
    optimisation_score = models.FloatField(null=True, blank=True)
    def __str__(self):
        return self.title
    
# Blackouts Dates Table
   
class BlackoutDate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=False, blank=False)
    end_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"Blackout from {self.start_date} to {self.end_date}"

# Onboarding Data Table
class OnboardingData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    survey_completion_date = models.DateTimeField(auto_now_add=True)
    survey_results = models.JSONField(null=False, blank=False)

    def __str__(self):
        return f"Onboarding data for {self.user.full_name if self.user.full_name else self.user.email}"
    
# Action Data Table
class ActionData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=False, blank=False)
    application_area_name = models.CharField(max_length=255, null=False, blank=False)
    action_description = models.TextField(null=False, blank=False)
    action_duration_seconds = models.PositiveIntegerField(null=False, blank=False)

    def __str__(self):
        return f"Action by {self.user.full_name if self.user and self.user.full_name else (self.user.email if self.user else 'Unknown')}"
    
# Wellbeing Score Table
class WellbeingScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(null=False, blank=False)
    score_type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Wellbeing score for {self.user.full_name if self.user.full_name else self.user.email} on {self.score_date}"
    
class PublicHoliday(models.Model):
    country_code = models.CharField(max_length=10, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.date})"
    

class GamificationData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.PositiveIntegerField(default=0)  # Total gamification points
    streak_days = models.PositiveIntegerField(default=0)  # Current streak of following breaks
    badges = models.JSONField(default=list)  # List of earned badges

    def __str__(self):
        return f"Gamification data for {self.user.full_name if self.user.full_name else self.user.email}"
    

class WellbeingQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_text = models.TextField(null=False, blank=False)
    score_type = models.CharField(max_length=100, null=False, blank=False)

# ----------------------------------------


class LeaveBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_balance",
        unique=True
    )
    anual_leave_balance = models.PositiveIntegerField(default=60)
    anual_leave_refresh_date = models.DateField()
    already_used_balance = models.PositiveIntegerField(default=0)

    updated_at = models.DateTimeField(auto_now=True)

    def refresh_balance_if_due(self):
        """Automatically refresh annual leave balance if today >= refresh date."""
        today = date.today()
        if today >= self.anual_leave_refresh_date:
            self.anual_leave_balance = 60
            self.already_used_balance = 0
            self.anual_leave_refresh_date = date(
                today.year + 1,
                self.anual_leave_refresh_date.month,
                self.anual_leave_refresh_date.day
            )
            self.save()

    def deduct_days(self, days):
        if days > self.anual_leave_balance:
            raise ValueError("Not enough leave balance")
        self.anual_leave_balance -= days
        self.already_used_balance += days
        self.save()

    def save(self, *args, **kwargs):
        self.refresh_balance_if_due()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.full_name if self.user.full_name else self.user.email} - {self.anual_leave_balance} days left"

# ----------------------------------------

class BreakPlan(models.Model):
    BREAK_TYPES = [
        ('vacation', 'Vacation'),
        ('sick', 'Sick'),
        ('personal', 'Personal'),
    ]

    BREAK_STATUSES = [
        ('planned', 'Planned'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    leave_balance = models.ForeignKey(
        LeaveBalance,
        on_delete=models.CASCADE,
        related_name="break_plans"
    )
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    description = models.TextField()
    type = models.CharField(max_length=20, choices=BREAK_TYPES)
    status = models.CharField(max_length=20, choices=BREAK_STATUSES, default='planned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """Deduct leave days when approved."""
        if self.status == 'approved':
            days_requested = (self.endDate.date() - self.startDate.date()).days + 1
            self.leave_balance.deduct_days(days_requested)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.full_name if self.user.full_name else self.user.email} - {self.type} ({self.startDate.date()} to {self.endDate.date()})"


# ======== USER - NOTIFICATION =======

class UserNotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    breaksReminder = models.BooleanField(default=True)
    suggestions = models.BooleanField(default=True)
    deadlineAlerts = models.BooleanField(default=True)
    weeklyDigest = models.BooleanField(default=True)
    pushEnabled = models.BooleanField(default=True)
    emailEnabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Notification preferences for {self.user.email}"


# ======== WORKING PATTHERN =======
class WorkingPattern(models.Model):
    PATTERN_TYPES = (
        ('standard', 'Standard (Mon-Fri)'),
        ('custom', 'Custom'),
        ('shift', 'Shift'),
    )

    ROTATION_CHOICES = (
        ('1_week', '1 Week Rotation'),
        ('2_weeks', '2 Weeks Rotation'),
        ('3_weeks', '3 Weeks Rotation'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="working_pattern")
    pattern_type = models.CharField(max_length=10, choices=PATTERN_TYPES)

    # Custom pattern
    custom_days = models.JSONField(blank=True, null=True, help_text="List of selected working days for custom pattern, e.g. ['Mon', 'Wed', 'Fri']")

    # Shift pattern
    days_on = models.PositiveSmallIntegerField(blank=True, null=True)
    days_off = models.PositiveSmallIntegerField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    rotation_pattern = models.CharField(max_length=10, choices=ROTATION_CHOICES, blank=True, null=True)
    shift_preview = models.JSONField(blank=True, null=True, help_text="List of ON/OFF values per rotation week, e.g. [['ON', 'ON', 'ON', 'OFF', 'OFF', 'OFF', 'OFF'], [...]]")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s {self.pattern_type} pattern"

# ======== OPTIMIZATION GOAL =======
class OptimizationGoal(models.Model):
    PREFERENCES = [
        ('long_breaks', 'Long Breaks'),
        ('extended_breaks', 'Extended Breaks'),
        ('avoid_peak_seasons', 'Avoid Peak Seasons'),
        ('frequent_breaks', 'Frequent Breaks'),
        ('prioritize_weekends', 'Prioritize Weekends'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='optimization_goals')
    preference = models.CharField(max_length=30, choices=PREFERENCES)

    class Meta:
        unique_together = ('user', 'preference')

    def __str__(self):
        return f"{self.user.full_name if self.user.full_name else self.user.email} - {self.get_preference_display()}"


class BreakPreferences(models.Model):
    PREFERENCES = [
        ('long_weekends', 'Long Weekends'),
        ('extended_breaks', 'Extended Breaks'),
        ('mix_of_both', 'Mix of Both'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='break_preferences'
    )
    preference = models.CharField(max_length=30, choices=PREFERENCES)
    weather_based_recommendation = models.BooleanField(default=False)
    to_be_confirmed = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Break Preference"
        verbose_name_plural = "Break Preferences"
        ordering = ['user']

    def __str__(self):
        return f"{self.user} - {self.get_preference_display()}"
    



class Mood(models.Model):
    MOOD_CHOICES = [
        ("happy", "Happy"),
        ("sad", "Sad"),
        ("angry", "Angry"),
        ("neutral", "Neutral"),
        ("excited", "Excited"),
        ("anxious", "Anxious"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="moods")
    mood_type = models.CharField(max_length=20, choices=MOOD_CHOICES)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.mood_type} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


##########################
# Events and bookings
###########################
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    capacity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="events/", blank=True, null=True)  # NEW field

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    booked_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.full_name if self.user.full_name else self.user.email} - {self.event.title}"


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    reference = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.reference} - {self.status}"
