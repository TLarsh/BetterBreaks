from django.db import models
from django.conf import settings
import uuid
from django.utils import timezone
from .user_models import User
from .booking_models import Booking


class Payment(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"
        PENDING = "PENDING"

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    reference = models.CharField(max_length=255)  # from Paystack/Stripe
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices)

    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Payment {self.reference} - {self.status}"
