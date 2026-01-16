from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from .user_models import User


############### Dates Table 
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
    
########## Blackouts Dates Table ###########
   
class BlackoutDate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(null=False, blank=False)
    end_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return f"Blackout from {self.start_date} to {self.end_date}"