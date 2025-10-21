from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from .user_models import User
from .event_models import Booking

class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    reference = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")], default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.reference} - {self.status}"
