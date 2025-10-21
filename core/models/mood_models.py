from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone

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