from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



schedule_get_schema = swagger_auto_schema(
    operation_summary="Retrieve user's full schedule",
    tags=["User Schedule"],
    responses={
        200: openapi.Response(
            description="Schedule retrieved successfully.",
        ),
        500: openapi.Response(description="Internal server error.")
    }
)

schedule_post_schema = swagger_auto_schema(
    operation_summary="Update user's full schedule",
    tags=["User Schedule"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "working_pattern": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "pattern_type": openapi.Schema(type=openapi.TYPE_STRING),
                    "days_on": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "days_off": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "start_date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                    "rotation_pattern": openapi.Schema(type=openapi.TYPE_STRING),
                    "shift_preview": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING)
                        )
                    )
                }
            ),
            "blackout_dates": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "start_date": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                        "end_date": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                        "description": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            "optimization_goals": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING)
            )
        },
        required=["working_pattern"]
    ),
    responses={
        200: openapi.Response(description="Schedule updated successfully."),
        400: openapi.Response(description="Validation failed."),
        500: openapi.Response(description="Internal server error."),
    }
)

