from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from ..serializers.weather_serializers import WeatherForecastDaySerializer
from ..utils.weather_utils import (
    fetch_6day_weather_forecast_openweathermap,
)
from ..docs.weather_docs import weather_forecast_schema



class WeatherForecastView(APIView):
    @weather_forecast_schema
    def get(self, request):
        lat = request.query_params.get("lat")
        lon = request.query_params.get("lon")
        if not lat or not lon:
            return Response({"detail": "lat and lon are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return Response({"detail": "lat and lon must be valid numbers."}, status=status.HTTP_400_BAD_REQUEST)
        forecast = fetch_6day_weather_forecast_openweathermap(lat, lon)
        serializer = WeatherForecastDaySerializer(forecast, many=True)
        return Response(serializer.data)