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