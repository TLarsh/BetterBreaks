from core.serializers.score_serializers import OptimizationScoreSerializer, StreakScoreSerializer
from drf_yasg.utils import swagger_auto_schema



# --- OptimizationListCreateView ---
optimization_list = swagger_auto_schema(
    operation_summary="Get all optimization scores",
    operation_description="Retrieve all optimization scores for the logged-in user.",
    responses={200: OptimizationScoreSerializer(many=True)},
)

optimization_create = swagger_auto_schema(
    operation_summary="Create a new optimization score",
    operation_description="Create a new optimization score entry for the logged-in user.",
    request_body=OptimizationScoreSerializer,
    responses={201: OptimizationScoreSerializer},
)

# --- OptimizationDetailView ---
optimization_retrieve = swagger_auto_schema(
    operation_summary="Get a specific optimization score",
    operation_description="Retrieve a single optimization score by its ID.",
    responses={200: OptimizationScoreSerializer},
)

optimization_update = swagger_auto_schema(
    operation_summary="Update a specific optimization score",
    operation_description="Update a single optimization score by its ID.",
    request_body=OptimizationScoreSerializer,
    responses={200: OptimizationScoreSerializer},
)

optimization_delete = swagger_auto_schema(
    operation_summary="Delete a specific optimization score",
    operation_description="Delete a single optimization score by its ID.",
    responses={204: "Deleted successfully"},
)

# --- OptimizationCalculateView ---
optimization_calculate = swagger_auto_schema(
    operation_summary="Calculate optimization score",
    operation_description="Calculate the user's optimization score based on break preferences and working pattern. "
                          "If a score exists for today, it will be updated.",
    responses={200: OptimizationScoreSerializer},
)



# --- Score Summary ---
score_summary = swagger_auto_schema(
    operation_summary="Get user's score summary",
    operation_description="Retrieve the user's total break score, highest streak, recent breaks, streak history, "
                          "and latest optimization score.",
    responses={200: "Summary with scores and streaks"}
)

# --- StreakListCreateView ---
streak_list = swagger_auto_schema(
    operation_summary="Get all streak scores",
    operation_description="Retrieve all streak scores for the logged-in user.",
    responses={200: StreakScoreSerializer(many=True)},
)

streak_create = swagger_auto_schema(
    operation_summary="Create a new streak score",
    operation_description="Create a new streak score entry for the logged-in user.",
    request_body=StreakScoreSerializer,
    responses={201: StreakScoreSerializer},
)

# --- StreakDetailView ---
streak_retrieve = swagger_auto_schema(
    operation_summary="Get a specific streak score",
    operation_description="Retrieve a single streak score by its ID.",
    responses={200: StreakScoreSerializer},
)

streak_update = swagger_auto_schema(
    operation_summary="Update a specific streak score",
    operation_description="Update a single streak score by its ID.",
    request_body=StreakScoreSerializer,
    responses={200: StreakScoreSerializer},
)

streak_delete = swagger_auto_schema(
    operation_summary="Delete a specific streak score",
    operation_description="Delete a single streak score by its ID.",
    responses={204: "Deleted successfully"},
)