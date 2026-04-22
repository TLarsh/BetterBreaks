from django.db import models
import uuid
from django.utils import timezone
from .event_models import Event
from django.db import models
from django.conf import settings


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING"
        PAID = "PAID"
        FAILED = "FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey("Event", on_delete=models.CASCADE)

    tickets = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.event}"

# class Booking(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
#     event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
#     booked_at = models.DateTimeField(auto_now_add=True)
#     is_paid = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.user.full_name if self.user.full_name else self.user.email} - {self.event.title}"
