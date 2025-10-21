from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status



first_login_setup_docs = swagger_auto_schema(
    operation_summary="First Login Setup",
    operation_description="Initial setup for LeaveBalance, Preferences, and optional BreakPlan.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "LeaveBalance": openapi.Schema(
                type=openapi.TYPE_OBJECT, 
                properties={
                    "anual_leave_balance": openapi.Schema(type=openapi.TYPE_INTEGER, example=60),
                    "anual_leave_refresh_date": openapi.Schema(type=openapi.FORMAT_DATE, example="2025-01-01"),
                    "already_used_balance": openapi.Schema(type=openapi.TYPE_INTEGER, example=0)
                },
                required=["anual_leave_balance", "anual_leave_refresh_date", "already_used_balance"]
            ),
            "Preferences": openapi.Schema(
                type=openapi.TYPE_OBJECT, 
                properties={
                    "preference": openapi.Schema(type=openapi.TYPE_STRING, example="long_weekends"),
                    "weather_based_recommendation": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                    "to_be_confirmed": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False)
                },
                required=["preference"]
            ),
            "BreakPlan": openapi.Schema(
                type=openapi.TYPE_OBJECT, 
                properties={
                    "startDate": openapi.Schema(type=openapi.FORMAT_DATETIME, example="2025-08-10T09:00:00Z"),
                    "endDate": openapi.Schema(type=openapi.FORMAT_DATETIME, example="2025-08-15T18:00:00Z"),
                    "description": openapi.Schema(type=openapi.TYPE_STRING, example="Summer vacation"),
                    "status": openapi.Schema(type=openapi.TYPE_STRING, example="planned"),
                    "type": openapi.Schema(type=openapi.TYPE_STRING, example="vacation")
                },
                required=["startDate", "endDate"]
            ),
        }
    ),
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            description="Setup completed successfully",
        ),
        status.HTTP_400_BAD_REQUEST: "Validation error"
    }
)