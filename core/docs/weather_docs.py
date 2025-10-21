from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


##### Weather Forecast Swagger #####


weather_forecast_params = [
    openapi.Parameter(
        'lat', openapi.IN_QUERY, description="Latitude", type=openapi.TYPE_NUMBER, required=True
    ),
    openapi.Parameter(
        'lon', openapi.IN_QUERY, description="Longitude", type=openapi.TYPE_NUMBER, required=True
    ),
]

weather_forecast_response = openapi.Response(
    description="8-day weather forecast",
    examples={
        "application/json": [
            {
                "dt": 1692979200,
                "sunrise": 1692957600,
                "sunset": 1693004400,
                "temp": {"day": 28.5, "min": 24.0, "max": 30.0},
                "weather": [{"id": 500, "main": "Rain", "description": "light rain"}],
                # ...other fields...
            },
            # ... up to 8 items ...
        ]
    }
)

weather_forecast_schema = swagger_auto_schema(
    manual_parameters=weather_forecast_params,
    responses={200: weather_forecast_response},
    operation_description="Get 8-day weather forecast for a given latitude and longitude."
)


