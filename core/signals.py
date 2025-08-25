# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.conf import settings
# from .models import LeaveBalance
# from datetime import date

# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_leave_balance(sender, instance, created, **kwargs):
#     if created and not LeaveBalance.objects.filter(user=instance).exists():
#         LeaveBalance.objects.create(
#             user=instance,
#             annual_leave_refresh_date=date.today()
#         )
