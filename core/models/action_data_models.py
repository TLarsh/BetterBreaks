from django.db import models
from .user_models import User
import uuid
from django.utils import timezone

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