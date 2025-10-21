from django.db import models
import uuid
from django.utils import timezone
from django.conf import settings
User = settings.AUTH_USER_MODEL


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