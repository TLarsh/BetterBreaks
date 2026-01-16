from django.db import models
from django.conf import settings
import uuid
from datetime import date
# from .user import User

######### Leave Balance Models #############################
class LeaveBalance(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_balance",
        unique=True
    )
    anual_leave_balance = models.PositiveIntegerField()
    anual_leave_refresh_date = models.DateField()
    already_used_balance = models.PositiveIntegerField()

    updated_at = models.DateTimeField(auto_now=True)

    def refresh_balance_if_due(self):
        
        today = date.today()
        if today >= self.anual_leave_refresh_date:
            original_total = self.anual_leave_balance + self.already_used_balance
            self.anual_leave_balance = original_total
            self.already_used_balance = 0
            self.anual_leave_refresh_date = date(
                today.year + 1,
                self.anual_leave_refresh_date.month,
                self.anual_leave_refresh_date.day
            )
            self.save(update_fields=["anual_leave_balance", "already_used_balance", "anual_leave_refresh_date"])

    def deduct_days(self, days: int):
        if days > self.anual_leave_balance:
            raise ValueError("Not enough leave balance")
        self.anual_leave_balance -= days
        self.already_used_balance += days
        self.save(update_fields=["anual_leave_balance", "already_used_balance"])

    def __str__(self):
        return f"{self.user.full_name if getattr(self.user, 'full_name', None) else self.user.email} - {self.anual_leave_balance} days left"
