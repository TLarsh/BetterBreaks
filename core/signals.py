from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import LeaveBalance

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_leave_balance(sender, instance, created, **kwargs):
    if created:
        LeaveBalance.objects.create(user=instance)



# class LeaveBalance(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name="leave_balance"
#     )
#     annual_leave_balance = models.PositiveIntegerField(default=60)
#     annual_leave_refresh_date = models.DateField()
#     already_used_balance = models.PositiveIntegerField(default=0)
#     updated_at = models.DateTimeField(auto_now=True)

#     def refresh_balance_if_due(self):
#         """Automatically refresh annual leave balance if today >= refresh date."""
#         today = date.today()
#         if today >= self.annual_leave_refresh_date:
#             self.annual_leave_balance = 60
#             self.already_used_balance = 0
#             self.annual_leave_refresh_date = date(
#                 today.year + 1,
#                 self.annual_leave_refresh_date.month,
#                 self.annual_leave_refresh_date.day
#             )
#             self.save()

#     def deduct_days(self, days):
#         """Deduct days from balance."""
#         if days > self.annual_leave_balance:
#             raise ValueError("Insufficient leave balance.")
#         self.annual_leave_balance -= days
#         self.already_used_balance += days
#         self.save()

#     def save(self, *args, **kwargs):
#         self.refresh_balance_if_due()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.user.username} - {self.annual_leave_balance} days"
# # ----------------------------------------

# class BreakPlan(models.Model):
#     BREAK_TYPES = [
#         ('vacation', 'Vacation'),
#         ('sick', 'Sick'),
#         ('personal', 'Personal'),
#     ]

#     BREAK_STATUSES = [
#         ('planned', 'Planned'),
#         ('pending', 'Pending'),
#         ('approved', 'Approved'),
#         ('rejected', 'Rejected'),
#     ]

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE
#     )
#     leave_balance = models.ForeignKey(
#         LeaveBalance,
#         on_delete=models.CASCADE,
#         related_name="break_plans"
#     )
#     startDate = models.DateTimeField()
#     endDate = models.DateTimeField()
#     description = models.TextField()
#     type = models.CharField(max_length=20, choices=BREAK_TYPES)
#     status = models.CharField(max_length=20, choices=BREAK_STATUSES, default='planned')
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         """Deduct leave days when approved."""
#         if self.status == 'approved':
#             days_requested = (self.endDate.date() - self.startDate.date()).days + 1
#             self.leave_balance.deduct_days(days_requested)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.user.username} - {self.type} ({self.startDate.date()} to {self.endDate.date()})"
    
# class BreakPreferences(models.Model):
#     PREFERENCES = [
#         ('long_weekends', 'Long Weekends'),
#         ('extended_breaks', 'Extended Breaks'),
#         ('mix_of_both', 'Mix of Both'),
#     ]

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='break_preferences'
#     )
#     preference = models.CharField(max_length=30, choices=PREFERENCES)
#     weather_based_recommendation = models.BooleanField(default=False)
#     to_be_confirmed = models.BooleanField(default=False)

#     class Meta:
#         verbose_name = "Break Preference"
#         verbose_name_plural = "Break Preferences"
#         ordering = ['user']

#     def __str__(self):
#         return f"{self.user} - {self.get_preference_display()}"

# ------------------
    
#     payload for setup on user's first login, get if already provided and create if not
# {
#     -LeaveBalance{
#         "annual_leave_balance":"",
#         "annual_leave_refresh_date":"",
#         "already_used_balance":

#     },
#     -Preferences{
#         "preference":"string",
#         "weather_based_recommendation":True,
#         "to_be_confirmed":True
#     },
#     -BreakPlan{
#         "startDAte":"",
#         "endDAte":"",
#         "description":"",
#         "status":"",
#         "type":""
#     }
# }

# for the BreakPlan startDate and endDate are required while other fields are optional  or if provided