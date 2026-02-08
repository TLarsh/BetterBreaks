from django.db import models
from .user_models import User
import uuid
from django.utils import timezone


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