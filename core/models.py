from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import date, timedelta
from django.utils.text import slugify
import uuid

# Gamification models are now included directly in this file

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
    
    # Gamification fields
    total_break_score = models.PositiveIntegerField(default=0)  # Accumulated break score
    total_badges = models.PositiveIntegerField(default=0)  # Total badges earned
    highest_streak = models.PositiveIntegerField(default=0)  # Highest streak achieved
    last_optimization_score = models.FloatField(default=0.0)  # Last optimization score

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
        from .models import PublicHolidayCalendar  # local import to avoid circulars

        calendar, _ = PublicHolidayCalendar.objects.get_or_create(
            user=self,
            defaults={"country_code": "US"}  # ✅ can be replaced with logic from timezone
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

####### Contact Messages Table #######################

class ContactMessage(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject or 'No Subject'}"


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
    


class SpecialDate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="special_dates"
    )
    title = models.CharField(max_length=255)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date"]
        unique_together = ("user", "date", "title")

    def __str__(self):
        return f"{self.title} - {self.date}"
    
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
# class OnboardingData(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     survey_completion_date = models.DateTimeField(auto_now_add=True)
#     survey_results = models.JSONField(null=False, blank=False)

#     def __str__(self):
#         return f"Onboarding data for {self.user.full_name if self.user.full_name else self.user.email}"
    
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
# class WellbeingScore(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     score_date = models.DateTimeField(auto_now_add=True)
#     score = models.IntegerField(null=False, blank=False)
#     score_type = models.CharField(max_length=100, null=True, blank=True)

#     def __str__(self):
#         return f"Wellbeing score for {self.user.full_name if self.user.full_name else self.user.email} on {self.score_date}"
    
class PublicHolidayCalendar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='holiday_calendar')
    country_code = models.CharField(max_length=10, null=False, blank=False, default='US')
    is_enabled = models.BooleanField(default=True)
    last_synced = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.email}'s holiday calendar - {self.country_code}"

class PublicHoliday(models.Model):
    country_code = models.CharField(max_length=10, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    google_calendar_event_id = models.CharField(max_length=255, null=True, blank=True)
    is_observed = models.BooleanField(default=False)  # Tracks if user took a break on this holiday
    calendar = models.ForeignKey(PublicHolidayCalendar, on_delete=models.CASCADE, related_name='holidays', null=True)

    class Meta:
        unique_together = ('date', 'country_code', 'calendar')
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date})"
    

############# Break Score Models #######################
class BreakScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='break_scores')
    score_date = models.DateField()
    score_value = models.PositiveIntegerField(default=0)
    frequency_points = models.PositiveIntegerField(default=0)  # Points for frequency of breaks
    adherence_points = models.PositiveIntegerField(default=0)  # Points for following recommended holidays
    wellbeing_impact = models.IntegerField(default=0)  # Impact on wellbeing (can be negative)
    break_type = models.CharField(max_length=50, choices=[
        ('holiday', 'Public Holiday'),
        ('weekend', 'Weekend'),
        ('personal', 'Personal Break'),
    ])
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'score_date')
        ordering = ['-score_date']
    
    def __str__(self):
        return f"{self.user.email}'s break score on {self.score_date} - {self.score_value} points"
    
    def calculate_total_score(self):
        """Calculate the total score based on component scores"""
        self.score_value = self.frequency_points + self.adherence_points + self.wellbeing_impact
        return self.score_value


########## STREAK SCORE MODELS #############################
class StreakScore(models.Model):
    STREAK_PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streak_scores')
    current_streak = models.PositiveIntegerField(default=0)  # Current consecutive streak count
    longest_streak = models.PositiveIntegerField(default=0)  # Longest streak achieved
    streak_period = models.CharField(max_length=20, choices=STREAK_PERIOD_CHOICES, default='monthly')
    last_break_date = models.DateField(null=True, blank=True)  # Date of the last break taken
    streak_start_date = models.DateField(null=True, blank=True)  # When the current streak started
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'streak_period')
    
    def __str__(self):
        return f"{self.user.email}'s {self.get_streak_period_display()} streak: {self.current_streak}"
    
    def increment_streak(self, break_date):
        """Increment the streak counter when a break is taken"""
        if not self.last_break_date:
            # First break ever
            self.current_streak = 1
            self.longest_streak = 1
            self.streak_start_date = break_date
        elif self._is_consecutive(break_date):
            # Consecutive break
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            # Break in streak, reset counter
            self.current_streak = 1
            self.streak_start_date = break_date
            
        self.last_break_date = break_date
        return self.current_streak
    
    def _is_consecutive(self, break_date):
        """Check if the break date maintains the streak based on the period"""
        if not self.last_break_date:
            return False
            
        if self.streak_period == 'weekly':
            # For weekly, breaks should be in consecutive weeks
            last_week = self.last_break_date.isocalendar()[1]
            current_week = break_date.isocalendar()[1]
            return (current_week - last_week == 1) or \
                   (last_week == 52 and current_week == 1)  # Year boundary
                   
        elif self.streak_period == 'monthly':
            # For monthly, breaks should be in consecutive months
            last_month = self.last_break_date.month
            current_month = break_date.month
            return (current_month - last_month == 1) or \
                   (last_month == 12 and current_month == 1)  # Year boundary
                   
        elif self.streak_period == 'yearly':
            # For yearly, breaks should be in consecutive years
            return break_date.year - self.last_break_date.year == 1
            
        return False

######## Badge Models #############################
class Badge(models.Model):
    BADGE_TYPES = [
        ('weekend_breaker', 'Weekend Breaker'),  # Taking breaks every weekend for a month
        ('holiday_master', 'Holiday Master'),     # Taking a break on every public holiday in a year
        ('consistent_breaker', 'Consistent Breaker'),  # Maintaining a 6-month streak
        ('break_pro', 'Break Pro'),              # Achieving high break scores
        ('wellness_warrior', 'Wellness Warrior'),  # Reporting positive wellbeing after breaks
        ('perfect_planner', 'Perfect Planner'),   # Planning breaks well in advance
        ('weekend_recharger', 'Weekend Recharger')  # Consistently taking weekend breaks
    ]
    
    BADGE_LEVELS = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum')
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge_type = models.CharField(max_length=50, choices=BADGE_TYPES)
    level = models.CharField(max_length=20, choices=BADGE_LEVELS, default='bronze')
    earned_date = models.DateField(auto_now_add=True)
    description = models.TextField()
    requirements_met = models.JSONField(default=dict)  # Store details about how badge was earned
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'badge_type', 'level')
        ordering = ['badge_type', 'level']
    
    def __str__(self):
        return f"{self.user.email}'s {self.get_level_display()} {self.get_badge_type_display()} Badge"


########## Optimization Score Models #############################
class OptimizationScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='optimization_scores')
    score_date = models.DateField()
    score_value = models.FloatField(default=0.0)  # Overall optimization score (0-100)
    break_timing_score = models.FloatField(default=0.0)  # Score for optimal break timing
    break_frequency_score = models.FloatField(default=0.0)  # Score for break frequency
    break_consistency_score = models.FloatField(default=0.0)  # Score for consistency
    notes = models.TextField(blank=True, null=True)
    recommendations = models.JSONField(default=list)  # List of personalized recommendations
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'score_date')
        ordering = ['-score_date']
    
    def __str__(self):
        return f"{self.user.email}'s optimization score on {self.score_date} - {self.score_value}"
    
    def calculate_total_score(self):
        """Calculate the total optimization score based on component scores"""
        # Weights for different components
        timing_weight = 0.4
        frequency_weight = 0.3
        consistency_weight = 0.3
        
        self.score_value = (
            self.break_timing_score * timing_weight +
            self.break_frequency_score * frequency_weight +
            self.break_consistency_score * consistency_weight
        )
        return self.score_value
    

# class WellbeingQuestion(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     question_text = models.TextField(null=False, blank=False)
#     score_type = models.CharField(max_length=100, null=False, blank=False)

# ----------------------------------------


# class LeaveBalance(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="leave_balance",
#         unique=True
#     )
#     anual_leave_balance = models.PositiveIntegerField()
#     anual_leave_refresh_date = models.DateField()
#     already_used_balance = models.PositiveIntegerField()

#     updated_at = models.DateTimeField(auto_now=True)

#     def refresh_balance_if_due(self):
#         """Automatically refresh annual leave balance if today >= refresh date."""
#         today = date.today()
#         if today >= self.anual_leave_refresh_date:
#             # Reset the balance to original value (total - used)
#             original_total = self.anual_leave_balance + self.already_used_balance
#             self.anual_leave_balance = original_total
#             self.already_used_balance = 0
#             self.anual_leave_refresh_date = date(
#                 today.year + 1,
#                 self.anual_leave_refresh_date.month,
#                 self.anual_leave_refresh_date.day
#             )
#             self.save()

#     def deduct_days(self, days):
#         if days > self.anual_leave_balance:
#             raise ValueError("Not enough leave balance")
#         self.anual_leave_balance -= days
#         self.already_used_balance += days
#         self.save()

#     def save(self, *args, **kwargs):
#         self.refresh_balance_if_due()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.user.full_name if self.user.full_name else self.user.email} - {self.anual_leave_balance} days left"

############ Break Plan Models #############################
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
        "LeaveBalance",
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
        """Deduct leave days when approved and update gamification scores."""
        is_new = self._state.adding
        old_status = None
        
        # If this is an existing object, get the old status
        if not is_new:
            try:
                old_instance = BreakPlan.objects.get(pk=self.pk)
                old_status = old_instance.status
            except BreakPlan.DoesNotExist:
                pass
        
        # Call the original save method
        super().save(*args, **kwargs)
        
        # If status changed to 'approved', update leave balance and create break score
        if self.status == 'approved' and old_status != 'approved':
            # Deduct leave days
            days_requested = (self.endDate.date() - self.startDate.date()).days + 1
            self.leave_balance.deduct_days(days_requested)
            
            # Create a BreakScore entry
            from django.utils import timezone
            break_type = 'personal'  # Default to personal break
            
            break_score, created = BreakScore.objects.get_or_create(
                user=self.user,
                score_date=self.startDate.date(),
                defaults={
                    'break_type': break_type,
                    'frequency_points': 10,  # Default points for taking a break
                    'adherence_points': 5,   # Default points for following the plan
                    'wellbeing_impact': 5,   # Default positive impact
                    'notes': f"Automatically logged from approved break plan: {self.description}"
                }
            )
            
            if created:
                # Calculate the total score
                break_score.calculate_total_score()
                break_score.save()
                
                # Update streak data
                streak, streak_created = StreakScore.objects.get_or_create(
                    user=self.user,
                    streak_period='monthly'  # Default to monthly streak
                )
                streak.increment_streak(self.startDate.date())
                streak.save()
                
                # Update user's total score if User model has these fields
                if hasattr(self.user, 'total_break_score'):
                    self.user.total_break_score += break_score.score_value
                    if hasattr(self.user, 'highest_streak') and streak.longest_streak > self.user.highest_streak:
                        self.user.highest_streak = streak.longest_streak
                    self.user.save(update_fields=['total_break_score', 'highest_streak'])
                
                # Update optimization score
                self._update_optimization_score()
    
    def _update_optimization_score(self):
        """Update the user's optimization score based on this break."""
        from django.utils import timezone
        today = timezone.now().date()
        
        # Try to get today's optimization score or create a new one
        opt_score, created = OptimizationScore.objects.get_or_create(
            user=self.user,
            score_date=today,
            defaults={
                'break_timing_score': 70.0,  # Default values
                'break_frequency_score': 70.0,
                'break_consistency_score': 70.0,
            }
        )
        
        # Increase break frequency score since user took a break
        opt_score.break_frequency_score = min(100.0, opt_score.break_frequency_score + 5.0)
        
        # Recalculate total score
        opt_score.calculate_total_score()
        opt_score.save()
        
        # Check if user qualifies for any badges
        self._check_and_award_badges()
        
    def _check_and_award_badges(self):
        """Check if the user qualifies for any badges based on their break patterns."""
        from django.utils import timezone
        from datetime import timedelta
        
        # Get user's break scores from the last 30 days
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        recent_breaks = BreakScore.objects.filter(
            user=self.user,
            score_date__gte=thirty_days_ago
        ).count()
        
        # Get user's streak information
        try:
            streak = StreakScore.objects.get(user=self.user, streak_period='monthly')
            current_streak = streak.current_streak
            longest_streak = streak.longest_streak
        except StreakScore.DoesNotExist:
            current_streak = 0
            longest_streak = 0
        
        # Check for Consistent Breaker badge (based on streak)
        if current_streak >= 3:  # If user has a streak of at least 3
            badge_level = 'bronze'
            if current_streak >= 6:
                badge_level = 'silver'
            if current_streak >= 12:
                badge_level = 'gold'
            if current_streak >= 24:
                badge_level = 'platinum'
                
            # Create or update the badge
            Badge.objects.get_or_create(
                user=self.user,
                badge_type='consistent_breaker',
                level=badge_level,
                defaults={
                    'description': f'Maintained a streak of {current_streak} consecutive monthly breaks',
                    'requirements_met': {'streak': current_streak}
                }
            )
        
        # Check for Break Pro badge (based on number of breaks)
        if recent_breaks >= 4:  # If user has taken at least 4 breaks in the last 30 days
            badge_level = 'bronze'
            if recent_breaks >= 8:
                badge_level = 'silver'
            if recent_breaks >= 12:
                badge_level = 'gold'
            if recent_breaks >= 20:
                badge_level = 'platinum'
                
            # Create or update the badge
            Badge.objects.get_or_create(
                user=self.user,
                badge_type='break_pro',
                level=badge_level,
                defaults={
                    'description': f'Took {recent_breaks} breaks in the last 30 days',
                    'requirements_met': {'recent_breaks': recent_breaks}
                }
            )
        
        # Check for Perfect Planner badge (based on planning breaks in advance)
        # This is a simple implementation - in a real system, you might want to check
        # how far in advance the break was planned
        badge_level = 'bronze'  # Start with bronze for planning any break
        
        # Create or update the badge
        Badge.objects.get_or_create(
            user=self.user,
            badge_type='perfect_planner',
            level=badge_level,
            defaults={
                'description': 'Planned and took a break successfully',
                'requirements_met': {'planned_breaks': 1}
            }
        )

    def __str__(self):
        return (
            f"{self.user.full_name if getattr(self.user, 'full_name', None) else self.user.email} "
            f"- {self.type} ({self.startDate.date()} to {self.endDate.date()})"
        )

# ----------------------------------------
######### Leave Balance Models #############################
class LeaveBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_balance",
        unique=True
    )
    anual_leave_balance = models.PositiveIntegerField()
    anual_leave_refresh_date = models.DateField()
    already_used_balance = models.PositiveIntegerField()

    updated_at = models.DateTimeField(auto_now=True)

    def refresh_balance_if_due(self):
        """
        Explicitly refresh annual leave balance if today >= refresh date.
        Must be called manually, not on every save().
        """
        today = date.today()
        if today >= self.anual_leave_refresh_date:
            original_total = self.anual_leave_balance + self.already_used_balance
            self.anual_leave_balance = original_total
            self.already_used_balance = 0
            self.anual_leave_refresh_date = date(
                today.year + 1,
                self.anual_leave_refresh_date.month,
                self.anual_leave_refresh_date.day
            )
            self.save(update_fields=["anual_leave_balance", "already_used_balance", "anual_leave_refresh_date"])

    def deduct_days(self, days: int):
        if days > self.anual_leave_balance:
            raise ValueError("Not enough leave balance")
        self.anual_leave_balance -= days
        self.already_used_balance += days
        self.save(update_fields=["anual_leave_balance", "already_used_balance"])

    def __str__(self):
        return f"{self.user.full_name if getattr(self.user, 'full_name', None) else self.user.email} - {self.anual_leave_balance} days left"


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

######## BREAK PREFERENCES #############################
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
    

####### MOOD TRACKER #################################
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
