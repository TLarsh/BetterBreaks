from django.db import models
from django.conf import settings
import uuid

User = settings.AUTH_USER_MODEL


class BreakExecution(models.Model):
    STATUS_CHOICES = [
        ("recommended", "Recommended"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("taken", "Taken"),
        ("missed", "Missed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="break_executions")

    recommended_start = models.DateField()
    recommended_end = models.DateField()

    actual_start = models.DateField(null=True, blank=True)
    actual_end = models.DateField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="recommended")

    optimisation_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def duration(self):
        if self.actual_start and self.actual_end:
            return (self.actual_end - self.actual_start).days + 1
        return 0

    def __str__(self):
        return f"{self.user} - {self.status}"
