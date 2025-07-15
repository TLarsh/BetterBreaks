from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings
import requests
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from .models import WellbeingScore, DateEntry, GamificationData
import random

def fetch_public_holidays(country_code, year):
    """
    Fetch public holidays for a specific country and year.
    """
    url = f"https://date.nager.at/api/v3/publicholidays/{year}/{country_code}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

def create_calendar_event(user, date_entry):
    """
    Creates a calendar event using Google Calendar API.
    Assumes OAuth credentials are stored in the User model.
    """
    # Authenticate with Google Calendar API
    credentials = Credentials(token=user.google_oauth_token)  # Ensure `google_oauth_token` is added to the User model
    service = build('calendar', 'v3', credentials=credentials)

    # Create the event payload
    event = {
        'summary': date_entry.title,
        'description': date_entry.description,
        'start': {'dateTime': date_entry.start_date.isoformat()},
        'end': {'dateTime': date_entry.end_date.isoformat()},
    }

    # Insert the event into the user's primary calendar
    event_result = service.events().insert(calendarId='primary', body=event).execute()

    # Update the DateEntry model with the calendar event ID
    date_entry.calendar_event_id = event_result['id']
    date_entry.event_status = "booked"
    date_entry.save()

from datetime import timedelta
from django.utils import timezone
from .models import WellbeingScore, DateEntry, GamificationData

def calculate_smart_planning_score(user):
    """
    Calculate the Smart Planning Score based on break adherence and engagement.
    """
    # Step 1: Count recent AI-recommended breaks followed
    recent_breaks = DateEntry.objects.filter(
        user=user,
        start_date__gte=timezone.now() - timedelta(days=30)
    ).count()

    # Step 2: Count recent wellbeing check-ins
    recent_check_ins = WellbeingScore.objects.filter(
        user=user,
        score_date__gte=timezone.now() - timedelta(days=30)
    ).count()

    # Step 3: Calculate the score (example formula)
    score = recent_breaks * 5 + recent_check_ins * 3
    return score

def award_badges(user):
    """
    Award badges based on user's gamification data.
    """
    gamification_data = GamificationData.objects.get_or_create(user=user)[0]

    # Example Badge Criteria
    if gamification_data.streak_days >= 30:
        if "Break Pro" not in gamification_data.badges:
            gamification_data.badges.append("Break Pro")
    if gamification_data.points >= 500:
        if "Wellness Warrior" not in gamification_data.badges:
            gamification_data.badges.append("Wellness Warrior")

    gamification_data.save()

def calculate_smart_planning_score(user):
    """
    Calculate the Smart Planning Score based on break adherence and engagement.
    """
    # Step 1: Count recent AI-recommended breaks followed
    recent_breaks = DateEntry.objects.filter(
        user=user,
        start_date__gte=timezone.now() - timedelta(days=30)
    ).count()

    # Step 2: Count recent wellbeing check-ins
    recent_check_ins = WellbeingScore.objects.filter(
        user=user,
        score_date__gte=timezone.now() - timedelta(days=30)
    ).count()

    # Step 3: Calculate the score (example formula)
    score = recent_breaks * 5 + recent_check_ins * 3
    return score

def award_badges(user):
    """
    Award badges based on user's gamification data.
    """
    gamification_data = GamificationData.objects.get_or_create(user=user)[0]

    # Example Badge Criteria
    if gamification_data.streak_days >= 30:
        if "Break Pro" not in gamification_data.badges:
            gamification_data.badges.append("Break Pro")
    if gamification_data.points >= 500:
        if "Wellness Warrior" not in gamification_data.badges:
            gamification_data.badges.append("Wellness Warrior")

    gamification_data.save()


def generate_holiday_suggestions(user):
    """
    Simulate generating holiday suggestions using BetterBreaksAI.
    Returns a list of suggested holidays with placeholders for missing data.
    """
    suggestions = []
    start_date = datetime.now() + timedelta(days=random.randint(7, 30))  # Random future date
    end_date = start_date + timedelta(days=random.randint(1, 7))  # Random duration (1-7 days)

    suggestions.append({
        "start_date": start_date,
        "end_date": end_date,
        "title": "Suggested Holiday",
        "description": "A relaxing break suggested by BetterBreaksAI.",
        "score": random.randint(50, 100),  # Placeholder score
    })

    return suggestions

def fetch_weather_data(latitude, longitude, date):
    """
    Fetch daily weather forecast from Apple WeatherKit for a specific date.
    """
    url = "https://api.weatherkit.apple.com/v1/weather"
    api_key = "your_apple_weatherkit_api_key"  # Replace with your actual API key
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "dailyStart": date.strftime("%Y-%m-%d"),
        "dailyEnd": date.strftime("%Y-%m-%d"),
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    return None

def adjust_score_based_on_weather(score, weather_data):
    """
    Adjust the holiday score based on weather conditions.
    """
    if not weather_data or "daily" not in weather_data:
        return score

    # Example: Penalize bad weather (e.g., rain, extreme temperatures)
    weather_conditions = weather_data["daily"][0]["conditionCode"]
    temperature_max = weather_data["daily"][0]["temperatureMax"]
    temperature_min = weather_data["daily"][0]["temperatureMin"]

    if weather_conditions in ["rain", "thunderstorms"]:
        score -= 20  # Penalize rainy days
    elif temperature_max > 35 or temperature_min < 5:
        score -= 15  # Penalize extreme temperatures

    return max(score, 0)  # Ensure score doesn't go below 0
