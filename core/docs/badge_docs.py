from drf_yasg.utils import swagger_auto_schema
from core.serializers.badge_serializers import BadgeSerializer



# --- BadgeListCreateView ---
badge_list = swagger_auto_schema(
    operation_summary="Get all badges",
    operation_description="Retrieve all badges earned by the logged-in user.",
    responses={200: BadgeSerializer(many=True)},
)

badge_create = swagger_auto_schema(
    operation_summary="Create a new badge",
    operation_description="Manually create a badge for the logged-in user.",
    request_body=BadgeSerializer,
    responses={201: BadgeSerializer},
)

# --- BadgeDetailView ---
badge_retrieve = swagger_auto_schema(
    operation_summary="Get a specific badge",
    operation_description="Retrieve details of a badge by its ID.",
    responses={200: BadgeSerializer},
)

badge_update = swagger_auto_schema(
    operation_summary="Update a specific badge",
    operation_description="Update a badge by its ID.",
    request_body=BadgeSerializer,
    responses={200: BadgeSerializer},
)

badge_delete = swagger_auto_schema(
    operation_summary="Delete a specific badge",
    operation_description="Delete a badge by its ID.",
    responses={204: "Deleted successfully"},
)

# --- BadgeEligibilityView ---
badge_eligibility = swagger_auto_schema(
    operation_summary="Check and award eligible badges",
    operation_description="Check if the logged-in user qualifies for new badges based on activity "
                          "and award them if eligible.",
    responses={200: BadgeSerializer(many=True)},
)