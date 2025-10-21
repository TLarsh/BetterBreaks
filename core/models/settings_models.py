from django.db import models
import uuid
from django.conf import settings
from .user_models import User
User = settings.AUTH_USER_MODEL



# User Settings Table

class UserSettings(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="settings")
    theme = models.CharField(max_length=10, choices=[('light', 'Light'), ('dark', 'Dark'), ('system', 'System')], default='system')
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    currency = models.CharField(max_length=10, default='USD')

    def __str__(self):
        return f"{self.user.email}'s settings"

#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     settings_json = models.JSONField(null=False, blank=False)

#     def __str__(self):
#         return f"Settings for {self.user.username}"