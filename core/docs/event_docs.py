from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.serializers.event_serializers import EventSerializer, BookingSerializer




# ---- Events ----
event_list_docs = swagger_auto_schema(
    operation_summary="List all events",
    operation_description="Retrieve all events with optional filters for title, location, and date range.",
    manual_parameters=[
        openapi.Parameter("title", openapi.IN_QUERY, description="Filter by title", type=openapi.TYPE_STRING),
        openapi.Parameter("location", openapi.IN_QUERY, description="Filter by location", type=openapi.TYPE_STRING),
        openapi.Parameter("start_date", openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        openapi.Parameter("end_date", openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
    ],
    responses={200: EventSerializer(many=True)}
)


# ---- Bookings ----
book_event_docs = swagger_auto_schema(
    operation_summary="Book an event",
    operation_description="Authenticated users can book an event by providing the event ID in the URL.",
    responses={201: BookingSerializer()}
)


