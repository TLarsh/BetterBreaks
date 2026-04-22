from rest_framework.exceptions import ValidationError
from ..utils.weather_utils import (
    fetch_6day_weather_forecast_openweathermap,
)



def get_coordinates(request):
    user = request.user

    if user.is_authenticated and getattr(user, "home_location_coordinates", None):
        try:
            lat_str, lon_str = user.home_location_coordinates.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            return lat, lon
        except (ValueError, AttributeError):
            raise ValidationError("Invalid format for user's home_location_coordinates.")

    # Fallback to query params
    lat = request.query_params.get("lat")
    lon = request.query_params.get("lon")

    if not lat or not lon:
        raise ValidationError("lat and lon are required.")

    try:
        return float(lat), float(lon)
    except ValueError:
        raise ValidationError("lat and lon must be valid numbers.")


def get_weather_forecast(request):
    lat, lon = get_coordinates(request)
    return fetch_6day_weather_forecast_openweathermap(lat, lon)