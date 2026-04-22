from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from ..serializers.weather_serializers import WeatherForecastDaySerializer
from ..utils.weather_utils import (
    fetch_6day_weather_forecast_openweathermap,
)
from ..services.weather_service import get_weather_forecast
from ..docs.weather_docs import weather_forecast_schema



class WeatherForecastView(APIView):
    @weather_forecast_schema
    def get(self, request):
        try:
            forecast = get_weather_forecast(request)
        except ValidationError as e:
            return Response({"detail": str(e.detail)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = WeatherForecastDaySerializer(forecast, many=True)
        return Response(serializer.data)