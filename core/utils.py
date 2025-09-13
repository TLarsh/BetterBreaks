from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings
from django.core.mail import send_mail,EmailMultiAlternatives, BadHeaderError
import requests
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
import pytz
import pycountry
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
# from .models import WellbeingScore, DateEntry, GamificationData
import random
from rest_framework.response import Response
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
import smtplib
import logging
load_dotenv()
logger = logging.getLogger(__name__)

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
from .models import (
    DateEntry, 
    # GamificationData,
    # WellbeingScore,
)

# def calculate_smart_planning_score(user):
#     """
#     Calculate the Smart Planning Score based on break adherence and engagement.
#     """
#     # Step 1: Count recent AI-recommended breaks followed
#     recent_breaks = DateEntry.objects.filter(
#         user=user,
#         start_date__gte=timezone.now() - timedelta(days=30)
#     ).count()

#     # Step 2: Count recent wellbeing check-ins
#     recent_check_ins = WellbeingScore.objects.filter(
#         user=user,
#         score_date__gte=timezone.now() - timedelta(days=30)
#     ).count()

#     # Step 3: Calculate the score (example formula)
#     score = recent_breaks * 5 + recent_check_ins * 3
#     return score

# def award_badges(user):
#     """
#     Award badges based on user's gamification data.
#     """
#     gamification_data = GamificationData.objects.get_or_create(user=user)[0]

#     # Example Badge Criteria
#     if gamification_data.streak_days >= 30:
#         if "Break Pro" not in gamification_data.badges:
#             gamification_data.badges.append("Break Pro")
#     if gamification_data.points >= 500:
#         if "Wellness Warrior" not in gamification_data.badges:
#             gamification_data.badges.append("Wellness Warrior")

#     gamification_data.save()

# def calculate_smart_planning_score(user):
#     """
#     Calculate the Smart Planning Score based on break adherence and engagement.
#     """
#     # Step 1: Count recent AI-recommended breaks followed
#     recent_breaks = DateEntry.objects.filter(
#         user=user,
#         start_date__gte=timezone.now() - timedelta(days=30)
#     ).count()

#     # Step 2: Count recent wellbeing check-ins
#     recent_check_ins = WellbeingScore.objects.filter(
#         user=user,
#         score_date__gte=timezone.now() - timedelta(days=30)
#     ).count()

#     # Step 3: Calculate the score (example formula)
#     score = recent_breaks * 5 + recent_check_ins * 3
#     return score

# def award_badges(user):
#     """
#     Award badges based on user's gamification data.
#     """
#     gamification_data = GamificationData.objects.get_or_create(user=user)[0]

#     # Example Badge Criteria
#     if gamification_data.streak_days >= 30:
#         if "Break Pro" not in gamification_data.badges:
#             gamification_data.badges.append("Break Pro")
#     if gamification_data.points >= 500:
#         if "Wellness Warrior" not in gamification_data.badges:
#             gamification_data.badges.append("Wellness Warrior")

#     gamification_data.save()


# def generate_holiday_suggestions(user):
#     """
#     Simulate generating holiday suggestions using BetterBreaksAI.
#     Returns a list of suggested holidays with placeholders for missing data.
#     """
#     suggestions = []
#     start_date = datetime.now() + timedelta(days=random.randint(7, 30))  # Random future date
#     end_date = start_date + timedelta(days=random.randint(1, 7))  # Random duration (1-7 days)

#     suggestions.append({
#         "start_date": start_date,
#         "end_date": end_date,
#         "title": "Suggested Holiday",
#         "description": "A relaxing break suggested by BetterBreaksAI.",
#         "score": random.randint(50, 100),  # Placeholder score
#     })

#     return suggestions

# def fetch_weather_data(latitude, longitude, date):
#     """
#     Fetch daily weather forecast from Apple WeatherKit for a specific date.
#     """
#     url = "https://api.weatherkit.apple.com/v1/weather"
#     api_key = "your_apple_weatherkit_api_key"  # Replace with your actual API key
#     headers = {
#         "Authorization": f"Bearer {api_key}",
#     }
#     params = {
#         "latitude": latitude,
#         "longitude": longitude,
#         "dailyStart": date.strftime("%Y-%m-%d"),
#         "dailyEnd": date.strftime("%Y-%m-%d"),
#     }

#     response = requests.get(url, headers=headers, params=params)
#     if response.status_code == 200:
#         return response.json()
#     return None


# def fetch_8day_weather_forecast_openweathermap(latitude, longitude):
#     """
#     Fetch 8-day daily weather forecast from OpenWeatherMap.
#     Returns a list of daily forecast dicts.
#     """
#     # api_key = "6291107705516e94ac5df05f71e1f5de"  # Replace with your actual API key
#     # url = "https://api.openweathermap.org/data/3.0/onecall" 
#     # url = "https://api.openweathermap.org/data/2.5/onecall" # Free tier endpoint
#     api_key = "dVVfPHo3rD9oENOkcvjKKQSQXoKLVzGn"  # Replace with your actual API key
#     url = "https://api.tomorrow.io/v4/weather/forecast"
#     params = {
#         "lat": latitude,
#         "lon": longitude,
#         "exclude": "minutely,hourly,alerts,current",
#         "units": "metric",
#         "appid": api_key,
#     }
#     response = requests.get(url, params=params)
#     print("Status:", response.status_code)
#     print("Response:", response.text)  
#     if response.status_code == 200:
#         data = response.json()
#         return data.get("daily", [])  # List of 8 daily forecast dicts
#     return []

def fetch_6day_weather_forecast_openweathermap(latitude, longitude):
    """
    Fetch 6-day daily weather forecast from OpenWeatherMap.
    Returns a list of daily forecast dicts.
    """
    # api_key = "6291107705516e94ac5df05f71e1f5de"  # Replace with your actual API key
    # url = "https://api.openweathermap.org/data/3.0/onecall" 
    # url = "https://api.openweathermap.org/data/2.5/onecall" # Free tier endpoint
    api_key = "dVVfPHo3rD9oENOkcvjKKQSQXoKLVzGn"  # Replace with your actual API key
    url = "https://api.tomorrow.io/v4/weather/forecast"
    params = {
        "location": f"{latitude},{longitude}",
        "timesteps": "1d",
        "apikey": api_key,
        "units": "metric",
    }
    response = requests.get(url, params=params)
    print("Status:", response.status_code)
    print("Response:", response.text)  
    if response.status_code == 200:
        data = response.json()
        # return data.get("daily", [])  # List of 8 daily forecast dicts
        return data.get("timelines", {}).get("daily", [])
    return []

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



# -------------------SEND EMAIL ------------

def send_otp_email(email, otp):
    try:
        brand_name = "Better Breaks"

        # Email subject & body
        subject = f"{brand_name} - Your Password Reset OTP"
        body = f"""
        <html>
            <body>
                <h2 style="color:#4CAF50;">{brand_name}</h2>
                <p>Hello,</p>
                <p>Your One-Time Password (OTP) for password reset is:</p>
                <h3 style="color:#ff6600;">{otp}</h3>
                <p>This code will expire in 10 minutes.</p>
                <br>
                <p>Thank you,</p>
                <p><strong>{brand_name} Team</strong></p>
            </body>
        </html>
        """

        # Email configuration
        from_email = settings.EMAIL_USER
        to_email = email

        # Create MIME message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{brand_name} <{from_email}>"
        msg["To"] = to_email
        msg.attach(MIMEText(body, "html"))

        # Decide between SSL or TLS
        if getattr(settings, "EMAIL_USE_SSL", False):
            server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)
        else:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            if getattr(settings, "EMAIL_USE_TLS", False):
                server.starttls()

        # Login & send
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.sendmail(from_email, [to_email], msg.as_string())
        server.quit()

        return True, f"OTP sent successfully to {email}"

    except smtplib.SMTPAuthenticationError:
        return False, "SMTP Authentication failed. Check your EMAIL_USER and EMAIL_PASSWORD."
    except smtplib.SMTPConnectError:
        return False, "SMTP Connection failed. Check EMAIL_HOST and EMAIL_PORT."
    except Exception as e:
        return False, f"Unexpected error while sending OTP: {str(e)}"




def normalize(value):
    """
    Normalize empty values to None
    """
    if value in [None, {}, [], ""]:
        return None
    return value

def success_response(message="", data=None, status_code=200):
    return Response({
        "message": message,
        "status": True,
        "data": normalize(data),
        "errors": None
    }, status=status_code)

def error_response(message="", errors=None, status_code=400):
    # Normalize all field values inside errors dict
    normalized_errors = {
        key: normalize(value)
        for key, value in (errors or {}).items()
    } if errors else None

    return Response({
        "message": message,
        "status": False,
        "data": None,
        "errors": normalized_errors
    }, status=status_code)



####### COUNTRY CODE RESOLUTION UTILITIES #######

tf = TimezoneFinder()
geolocator = Nominatim(user_agent="holiday-sync")

def timezone_to_country_code(timezone_str: str) -> str:
    """
    Convert timezone (e.g. 'Europe/Berlin') to country code (e.g. 'DE').
    Falls back to 'US' if not found.
    """
    try:
        if not timezone_str:
            return "US"

        for country_code, timezones in pytz.country_timezones.items():
            if timezone_str in timezones:
                return country_code.upper()

        return "US"
    except Exception:
        return "US"


def coords_to_country_code(coords: str) -> str:
    """
    Convert coordinates string ('lat,long') to country code.
    Uses geopy + Nominatim.
    """
    try:
        if not coords:
            return "US"

        lat, lng = map(float, coords.split(","))
        location = geolocator.reverse((lat, lng), language="en", timeout=10)

        if location and "country_code" in location.raw["address"]:
            return location.raw["address"]["country_code"].upper()

        return "US"
    except Exception:
        return "US"


def resolve_country_code(timezone_str: str, coords: str) -> str:
    """
    Resolve the most accurate country code:
    1. From timezone
    2. From coordinates
    3. Fallback 'US'
    """
    if timezone_str:
        code = timezone_to_country_code(timezone_str)
        if code != "US":  # Only fallback if unresolved
            return code

    if coords:
        return coords_to_country_code(coords)

    return "US"
