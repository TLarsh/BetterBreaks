from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from .user_models import User
from .badge_models import Badge
from .leave_balance_models import LeaveBalance
from .score_models import BreakScore, StreakScore, OptimizationScore



############ Break Plan Models #############################
class BreakPlan(models.Model):
    BREAK_TYPES = [
        ('vacation', 'Vacation'),
        ('sick', 'Sick'),
        ('personal', 'Personal'),
    ]

    BREAK_STATUSES = [
        ('planned', 'Planned'),     # created but not yet pending (draft)
        ('pending', 'Pending'),     # user submitted, waiting manager approval
        ('approved', 'Approved'),   # manager approved
        ('rejected', 'Rejected'),   # manager rejected
        ('taken', 'Taken'),         # user confirmed taken (or auto-confirmed)
        ('missed', 'Missed'),       # approved but not taken (auto-marked)
        ('cancelled', 'Cancelled'), # user cancelled before start
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
        """Handle break lifecycle and update gamification scores."""
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
        
        # If status changed to 'approved', update leave balance
        if self.status == 'approved' and old_status != 'approved':
            # No deduction yet, only when break is taken
            pass
            
        # If status changed to 'taken', deduct leave balance and update gamification positively
        elif self.status == 'taken' and old_status != 'taken':
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
                    'notes': f"Break taken: {self.description}"
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
        
        # If status changed to 'missed', update gamification negatively
        elif self.status == 'missed' and old_status != 'missed':
            # Reset streak
            streak, streak_created = StreakScore.objects.get_or_create(
                user=self.user,
                streak_period='monthly'  # Default to monthly streak
            )
            streak.current_streak = 0
            streak.streak_start_date = None
            streak.save()
            
            # Create a negative break score
            break_score, created = BreakScore.objects.get_or_create(
                user=self.user,
                score_date=self.startDate.date(),
                defaults={
                    'break_type': 'personal',
                    'frequency_points': 0,
                    'adherence_points': -5,  # Negative points for missing
                    'wellbeing_impact': -5,  # Negative impact
                    'notes': f"Break missed: {self.description}"
                }
            )
            
            if created:
                break_score.calculate_total_score()
                break_score.save()
                
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
            Badge.objects.get_or_create(
                user=self.user,
                badge_type='consistent_breaker',
                defaults={
                    'description': f'Maintained a streak of {current_streak} consecutive monthly breaks',
                    'requirements_met': {'streak': current_streak}
                }
            )
        
        # Check for Break Pro badge (based on number of breaks)
        if recent_breaks >= 4:  # If user has taken at least 4 breaks in the last 30 days
            Badge.objects.get_or_create(
                user=self.user,
                badge_type='break_pro',
                defaults={
                    'description': f'Took {recent_breaks} breaks in the last 30 days',
                    'requirements_met': {'recent_breaks': recent_breaks}
                }
            )
        
        # Check for Perfect Planner badge (based on planning breaks in advance)
        # This is a simple implementation - in a real system, you might want to check
        # how far in advance the break was planned
        Badge.objects.get_or_create(
            user=self.user,
            badge_type='perfect_planner',
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


# Break Suggestion model for personalized break recommendations
class BreakSuggestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='break_suggestions')
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255, help_text="Reason for suggesting this break")
    priority = models.IntegerField(default=0, help_text="Higher number means higher priority")
    is_accepted = models.BooleanField(null=True, blank=True, help_text="Whether user accepted this suggestion")
    based_on_mood = models.BooleanField(default=False)
    based_on_workload = models.BooleanField(default=False)
    based_on_preferences = models.BooleanField(default=False)
    based_on_weather = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ["-priority", "-created_at"]
    
    def __str__(self):
        return f"Break suggestion for {self.user.email}: {self.title} ({self.start_date} to {self.end_date})"
