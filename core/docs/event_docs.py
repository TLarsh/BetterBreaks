from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from core.serializers.event_serializers import EventSerializer, BookingSerializer


create_event_docs = swagger_auto_schema(
    # method="post",
    request_body=EventSerializer,
    responses={
        201: openapi.Response(
            description="Event created successfully",
            schema=EventSerializer
        )
    }
)

# ---- Events ----
# event_list_docs = swagger_auto_schema(
#     operation_summary="List all events",
#     operation_description="Retrieve all events with optional filters for title, location, and date range.",
#     manual_parameters=[
#         openapi.Parameter("title", openapi.IN_QUERY, description="Filter by title", type=openapi.TYPE_STRING),
#         openapi.Parameter("location", openapi.IN_QUERY, description="Filter by location", type=openapi.TYPE_STRING),
#         openapi.Parameter("start_date", openapi.IN_QUERY, description="Filter by start date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
#         openapi.Parameter("end_date", openapi.IN_QUERY, description="Filter by end date (YYYY-MM-DD)", type=openapi.TYPE_STRING),
#     ],
#     responses={200: EventSerializer(many=True)}
# )


event_list_docs = swagger_auto_schema(
    operation_description="Retrieve events with filters (title, location, category, date range, price range)",

    manual_parameters=[
        openapi.Parameter(
            'title',
            openapi.IN_QUERY,
            description="Search by event title",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'location',
            openapi.IN_QUERY,
            description="Filter by location",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'category',
            openapi.IN_QUERY,
            description="Filter by a single category",
            type=openapi.TYPE_STRING
        ),
        openapi.Parameter(
            'categories',
            openapi.IN_QUERY,
            description="Filter by multiple categories (repeat param)",
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_STRING),
            collectionFormat='multi'
        ),
        openapi.Parameter(
            'start_date',
            openapi.IN_QUERY,
            description="Start date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'end_date',
            openapi.IN_QUERY,
            description="End date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE
        ),
        openapi.Parameter(
            'min_price',
            openapi.IN_QUERY,
            description="Minimum price",
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_FLOAT
        ),
        openapi.Parameter(
            'max_price',
            openapi.IN_QUERY,
            description="Maximum price",
            type=openapi.TYPE_NUMBER,
            format=openapi.FORMAT_FLOAT
        ),
    ],

    responses={
        200: openapi.Response(
            description="Events retrieved successfully"
        )
    }
)


update_event_docs = swagger_auto_schema(
    request_body=EventSerializer,
    responses={
        200: openapi.Response(
            description="Event updated successfully",
            schema=EventSerializer
        )
    }
)

partial_update_event_docs = swagger_auto_schema(
    request_body=EventSerializer,
    responses={
        200: openapi.Response(
            description="Event partially updated successfully",
            schema=EventSerializer
        )
    }
)

delete_event_docs = swagger_auto_schema(
    operation_description="Delete an event by ID",
    responses={
        200: openapi.Response(description="Event deleted successfully"),
        404: openapi.Response(description="Event not found")
    }
)

# ---- Bookings ----
book_event_docs = swagger_auto_schema(
    operation_summary="Book an event",
    operation_description="Authenticated users can book an event by providing the event ID in the URL.",
    responses={201: BookingSerializer()}
)


