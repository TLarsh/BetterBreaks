from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from core.serializers.mood_serializers import MoodCheckInSerializer, MoodHistorySerializer



# Swagger for Mood Check-in
mood_checkin_schema = swagger_auto_schema(
    # method="post",
    tags=["Mood Tracking"],
    operation_summary="Mood Check-In",
    operation_description="Record the user's current mood with an optional note.",
    request_body=MoodCheckInSerializer,
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description="Mood check-in successful",
            schema=MoodCheckInSerializer
        ),
        status.HTTP_400_BAD_REQUEST: "Validation error"
    }
)

# Swagger for Mood History
mood_history_schema = swagger_auto_schema(
    # method="get",
    tags=["Mood Tracking"],
    operation_summary="Retrieve Mood History",
    operation_description="Get the mood history for the authenticated user. Optionally filter by start_date and end_date (YYYY-MM-DD).",
    manual_parameters=[
        openapi.Parameter(
            "start_date",
            openapi.IN_QUERY,
            description="Filter moods from this date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            "end_date",
            openapi.IN_QUERY,
            description="Filter moods until this date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING
        ),
    ],
    responses={
        status.HTTP_200_OK: openapi.Response(
            description="Mood history retrieved successfully",
            schema=MoodHistorySerializer(many=True)
        )
    }
)