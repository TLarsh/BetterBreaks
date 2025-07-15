from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
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
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username
# User Settings Table

class UserSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    settings_json = models.JSONField(null=False, blank=False)

    def __str__(self):
        return f"Settings for {self.user.username}"
    
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
    client = models.ForeignKey("Client", on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    token_valid = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.email} - {self.login_date}"
    
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
        return f"Onboarding data for {self.user.username}"
    
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
        return f"Action by {self.user.username if self.user else 'Unknown'}"
    
# Wellbeing Score Table
class WellbeingScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField(null=False, blank=False)
    score_type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Wellbeing score for {self.user.username} on {self.score_date}"
    
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
        return f"Gamification data for {self.user.username}"
    

class WellbeingQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_text = models.TextField(null=False, blank=False)
    score_type = models.CharField(max_length=100, null=False, blank=False)
