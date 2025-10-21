from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from .user_models import User


########## BREAK SCORE MODELS #############################

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