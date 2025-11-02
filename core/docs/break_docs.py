from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from core.serializers.score_serializers import BreakScoreSerializer
from core.serializers.break_serializers import BreakRecommendationSerializer, BreakPlanSerializer
# from core.models.preference_models import BreakPreference


# --- BreakLogListCreateView Swagger decorators ---

break_log_list = swagger_auto_schema(
    operation_summary="Get all break logs",
    operation_description="Retrieve all break logs (BreakScore records) for the currently logged-in user.",
    responses={200: BreakScoreSerializer(many=True)},
)

break_log_create = swagger_auto_schema(
    operation_summary="Log a new break",
    operation_description=(
        "Create a new BreakScore entry for the logged-in user. "
        "Also updates streak data and the user's total break score."
    ),
    request_body=BreakScoreSerializer,
    responses={201: BreakScoreSerializer},
)


# --- BreakLogDetailView Swagger ---

break_log_retrieve = swagger_auto_schema(
    operation_summary="Get a specific break log",
    operation_description="Retrieve a BreakScore entry by its ID (must belong to the logged-in user).",
    responses={200: BreakScoreSerializer},
)

break_log_update = swagger_auto_schema(
    operation_summary="Update a specific break log",
    operation_description="Update an existing BreakScore entry by ID (must belong to the logged-in user).",
    request_body=BreakScoreSerializer,
    responses={200: BreakScoreSerializer},
)

break_log_delete = swagger_auto_schema(
    operation_summary="Delete a specific break log",
    operation_description="Delete an existing BreakScore entry by ID (must belong to the logged-in user).",
    responses={204: "Deleted successfully"},
)

break_plan_action = swagger_auto_schema(
        operation_summary="Update break plan status",
        operation_description="Approve, reject, take, miss, or cancel a break plan.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'action': openapi.Schema(type=openapi.TYPE_STRING, description='Action to perform (approve, reject, take, miss, cancel)'),
                'reason': openapi.Schema(type=openapi.TYPE_STRING, description='Optional reason for the action'),
            },
            required=['action'],
        ),
        responses={
            200: openapi.Response(
                description="Break plan updated successfully",
                examples={
                    "application/json": {
                        "message": "Break successfully approved",
                        "data": {
                            # Example break plan data here
                        }
                    }
                }
            ),
            400: "Invalid action",
            404: "Break plan not found",
            500: "Failed to update break plan"
        }
    )






recommend_breaks_schema = swagger_auto_schema(
    request_body=BreakRecommendationSerializer,
    responses={
        200: openapi.Response(
            description="Break recommendation generated successfully."
        ),
        400: "Invalid input",
        500: "Internal server error"
    },
    operation_summary="Generate personalized break recommendations",
    operation_description=(
        "This endpoint uses ML models to predict ideal break duration and "
        "seasonal preferences based on user input."
    ),
    tags=["Break Recommendations"]
)