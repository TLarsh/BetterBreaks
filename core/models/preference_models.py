from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL

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
    



    
########## USER - NOTIFICATION ############################

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

