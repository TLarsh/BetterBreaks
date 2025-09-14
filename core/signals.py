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
import logging
from .models import PublicHolidayCalendar
from .tasks import sync_user_holidays

logger = logging.getLogger(__name__)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_calendar_and_sync(sender, instance, created, **kwargs):
    """
    Ensure every user has a holiday calendar and queue sync.
    Runs when a user is created or updated.
    """
    logger.info(f"Signal triggered for user {instance.id} - created: {created}")

    try:
        # Always get or create the calendar through the helper
        calendar = instance.get_calendar()

        # If user just created, pick country_code from timezone if possible
        if created and instance.home_location_timezone:
            try:
                tz_parts = instance.home_location_timezone.split('/')
                if len(tz_parts) > 1:
                    region = tz_parts[0]
                    city = tz_parts[1]

                    # Very simplified mapping — you can expand
                    if region == "America":
                        calendar.country_code = "US"
                    elif region == "Europe":
                        if "London" in city:
                            calendar.country_code = "GB"
                        elif "Paris" in city or "Berlin" in city:
                            calendar.country_code = "DE"
                        elif "Madrid" in city:
                            calendar.country_code = "ES"
                        elif "Rome" in city:
                            calendar.country_code = "IT"
                calendar.save(update_fields=["country_code"])
                logger.info(f"Country code set to {calendar.country_code} for user {instance.id}")
            except Exception as e:
                logger.warning(f"Could not map timezone {instance.home_location_timezone} for user {instance.id}: {e}")

        # Always queue sync if calendar has a country_code
        if calendar.country_code:
            task = sync_user_holidays.delay(instance.id, calendar.country_code)
            logger.info(f"Celery task queued (ID: {task.id}) for user {instance.id}")
        else:
            logger.warning(f"No country code set for user {instance.id}'s calendar")

    except Exception as e:
        logger.error(f"Error ensuring calendar for user {instance.id}: {str(e)}")