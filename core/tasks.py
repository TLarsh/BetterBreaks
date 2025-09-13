import requests
from celery import shared_task
from django.utils.timezone import now
from .models import User, PublicHoliday, PublicHolidayCalendar

@shared_task
def sync_user_holidays(user_id, country_code):
    """
    Fetch public holidays for current and next year from Nager.Date API
    and store them in PublicHoliday table.
    """
    try:
        user = User.objects.get(id=user_id)
        calendar = user.holiday_calendar

        if not calendar or not calendar.is_enabled:
            return f"No active holiday calendar for {user.email}"

        current_year = now().year
        years_to_fetch = [current_year, current_year + 1]

        for year in years_to_fetch:
            api_url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}"

            try:
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                holidays_data = response.json()
            except Exception as e:
                return f"Failed to fetch holidays for {year} ({country_code}): {str(e)}"

            for holiday in holidays_data:
                PublicHoliday.objects.update_or_create(
                    calendar=calendar,
                    country_code=country_code,
                    date=holiday["date"],
                    defaults={
                        "name": holiday.get("localName", holiday.get("name", "Holiday")),
                    },
                )

        calendar.last_synced = now()
        calendar.save(update_fields=["last_synced"])

        return f"Holidays synced successfully for {user.email} ({country_code})"

    except User.DoesNotExist:
        return f"User {user_id} does not exist"
    except Exception as e:
        return f"Failed syncing holidays for user {user_id}: {str(e)}"


@shared_task
def refresh_all_user_holidays():
    """
    Periodic task to refresh holidays for all users once per month.
    """
    current_year = now().year
    processed_users = []

    for user in User.objects.filter(holiday_calendar__is_enabled=True):
        country_code = user.holiday_calendar.country_code
        if not country_code:
            continue

        sync_user_holidays.delay(user.id, country_code)
        processed_users.append(user.email)

    return f"Triggered holiday sync for {len(processed_users)} users"
