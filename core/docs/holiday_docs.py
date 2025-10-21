from drf_yasg.utils import swagger_auto_schema
from core.serializers.holiday_serializers import PublicHolidaySerializer



# --- HolidayDetailView Swagger decorators ---

holiday_detail_get = swagger_auto_schema(
    operation_summary="Get a specific holiday",
    operation_description="Retrieve details of a holiday by its ID, only if it belongs to the logged-in user's holiday calendar.",
    responses={
        200: PublicHolidaySerializer,
        404: "Holiday not found",
    },
)

holiday_detail_put = swagger_auto_schema(
    operation_summary="Update a specific holiday",
    operation_description="Update details of an existing holiday by ID, only if it belongs to the logged-in user's holiday calendar.",
    request_body=PublicHolidaySerializer,
    responses={
        200: PublicHolidaySerializer,
        400: "Validation error",
        404: "Holiday not found",
    },
)

holiday_detail_delete = swagger_auto_schema(
    operation_summary="Delete a specific holiday",
    operation_description="Delete a holiday by its ID, only if it belongs to the logged-in user's holiday calendar.",
    responses={
        204: "Holiday deleted successfully",
        404: "Holiday not found",
    },
)



# --- UpcomingHolidaysView Swagger decorator ---

upcoming_holidays_get = swagger_auto_schema(
    operation_summary="Get upcoming holidays",
    operation_description=(
        "Retrieve the next 10 upcoming holidays from the logged-in user's holiday calendar. "
        "Results are ordered by date in ascending order."
    ),
    responses={200: PublicHolidaySerializer(many=True)},
)