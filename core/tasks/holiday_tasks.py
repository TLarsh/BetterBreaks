import requests
import logging
from celery import shared_task
from django.utils.timezone import now
from django.conf import settings
# from .models import User, PublicHoliday, PublicHolidayCalendar
from core.models.holiday_models import PublicHolidayCalendar, PublicHoliday
User = settings.AUTH_USER_MODEL

logger = logging.getLogger(__name__)

@shared_task
def sync_user_holidays(user_id, country_code):
    """
    Fetch public holidays for current and next year from Nager.Date API
    and store them in PublicHoliday table tied to the user's calendar.
    """
    logger.info(f"Starting sync_user_holidays task for user_id={user_id}, country_code={country_code}")
    try:
        user = User.objects.get(id=user_id)
        calendar = user.holiday_calendar
        logger.info(f"Found user {user.email}")

        if not calendar or not calendar.is_enabled:
            logger.warning(f"No active holiday calendar for {user.email}")
            return f"No active holiday calendar for {user.email}"

        current_year = now().year
        years_to_fetch = [current_year, current_year + 1]
        logger.info(f"Fetching holidays for years: {years_to_fetch}")

        #  Clear out old holidays for this calendar (avoid duplicates if country changes)
        calendar.holidays.all().delete()

        created_count = 0
        updated_count = 0
        for year in years_to_fetch:
            api_url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"
            logger.info(f"Fetching holidays from: {api_url}")

            try:
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                holidays_data = response.json()
                logger.info(f"Successfully fetched {len(holidays_data)} holidays for {year}")
            except Exception as e:
                logger.error(f"Failed to fetch holidays for {year} ({country_code}): {str(e)}")
                return f"Failed to fetch holidays for {year} ({country_code}): {str(e)}"

            for holiday in holidays_data:
                _, created = PublicHoliday.objects.update_or_create(
                    calendar=calendar,
                    country_code=country_code,
                    date=holiday["date"],
                    defaults={
                        "name": holiday.get("localName", holiday.get("name", "Holiday")),
                        "user": user,  # link back to user as well
                    },
                )
                if created:
                    created_count += 1
                else:
                    updated_count += 1

        logger.info(f"Created {created_count} and updated {updated_count} holidays for user_id={user_id}")
        calendar.last_synced = now()
        calendar.save(update_fields=["last_synced"])
        logger.info(f"Updated last_synced timestamp for user_id={user_id}")

        return f"Holidays synced successfully for {user.email} ({country_code})"

    except User.DoesNotExist:
        logger.error(f"User {user_id} does not exist")
        return f"User {user_id} does not exist"
    except Exception as e:
        logger.error(f"Failed syncing holidays for user {user_id}: {str(e)}")
        return f"Failed syncing holidays for user {user_id}: {str(e)}"


@shared_task
def refresh_all_user_holidays():
    """Refresh holidays for all users with enabled holiday calendars."""
    logger.info("Starting refresh_all_user_holidays task")
    
    try:
        calendars = PublicHolidayCalendar.objects.filter(is_enabled=True)
        logger.info(f"Found {calendars.count()} enabled holiday calendars")
        
        task_count = 0
        for calendar in calendars:
            if calendar.country_code:
                task = sync_user_holidays.delay(calendar.user_id, calendar.country_code)
                logger.info(f"Queued sync task {task.id} for user {calendar.user_id} with country {calendar.country_code}")
                task_count += 1
            else:
                logger.warning(f"Calendar for user {calendar.user_id} has no country code")
        
        logger.info(f"Successfully queued {task_count} sync tasks")
        return f"Refreshed holidays for {calendars.count()} users"
    except Exception as e:
        logger.error(f"Error in refresh_all_user_holidays: {str(e)}")
        return f"Error refreshing holidays: {str(e)}"
