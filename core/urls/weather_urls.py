from django.urls import path
from ..views.weather_views import WeatherForecastView

urlpatterns = [
    path("api/weather/forecast/", WeatherForecastView.as_view(), name="weather-forecast"),
]