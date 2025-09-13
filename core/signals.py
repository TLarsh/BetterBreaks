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


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import PublicHolidayCalendar
from .tasks import sync_user_holidays

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_calendar_and_sync(sender, instance, created, **kwargs):
    if created:
        calendar, _ = PublicHolidayCalendar.objects.get_or_create(
            user=instance,
            defaults={"country_code": "US"}  # fallback default, change if needed
        )

        if calendar.country_code:
            sync_user_holidays.delay(instance.id, calendar.country_code)
