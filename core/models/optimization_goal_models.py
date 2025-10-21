from django.db import models
from .user_models import User


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