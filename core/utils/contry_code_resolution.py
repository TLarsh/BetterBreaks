from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz



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





tf = TimezoneFinder()

def detect_timezone_from_coords(coords: str) -> str:
    """
    Convert coordinates to timezone string.
    """
    try:
        if not coords:
            return None

        lat, lng = map(float, coords.split(","))
        timezone_str = tf.timezone_at(lat=lat, lng=lng)

        return timezone_str
    except Exception:
        return None
    


def update_user_location(user, timezone=None, coords=None):
    updated = False

    
    if coords and not timezone:
        timezone = detect_timezone_from_coords(coords)

    if timezone and not user.home_location_timezone:
        user.home_location_timezone = timezone
        updated = True

    if coords and not user.home_location_coordinates:
        user.home_location_coordinates = coords
        updated = True

    if updated:
        user.save(update_fields=[
            "home_location_timezone",
            "home_location_coordinates"
        ])


        user.resolve_and_save_country_code()