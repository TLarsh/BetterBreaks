from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import requests
# import logging


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