from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers.date_serializers import DateEntrySerializer
from ..models.date_models import DateEntry
from ..utils.calendar_utils import create_calendar_event  
from ..models.event_models import Event
from ..models.booking_models import Booking
from ..serializers.event_serializers import EventSerializer, BookingSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..docs.event_docs import event_list_docs, book_event_docs 
  



# class BookEventView(APIView):
#     @swagger_auto_schema(request_body=DateEntrySerializer)
#     def post(self, request, date_entry_id):
#         try:
#             date_entry = DateEntry.objects.get(id=date_entry_id, user=request.user)
#             create_calendar_event(request.user, date_entry)
#             return Response({"success": True}, status=status.HTTP_200_OK)
#         except DateEntry.DoesNotExist:
#             return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)
        



#######################
# ======= EVENTS & BOOKINGS =======
#######################
class EventListView(APIView):
    permission_classes = [AllowAny]

    @event_list_docs
    def get(self, request):
        events = Event.objects.all()

        # Filters
        title = request.query_params.get("title")
        location = request.query_params.get("location")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        if title:
            events = events.filter(title__icontains=title)
        if location:
            events = events.filter(location__icontains=location)
        if start_date and end_date:
            events = events.filter(start_date__gte=start_date, end_date__lte=end_date)

        serializer = EventSerializer(events, many=True)
        return Response({
            "message": "Events retrieved successfully",
            "status": True,
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)


class BookEventView(APIView):
    permission_classes = [IsAuthenticated]

    @book_event_docs
    def post(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)
        booking = Booking.objects.create(user=request.user, event=event)
        serializer = BookingSerializer(booking)

        return Response({
            "message": "Event booked successfully. Proceed to payment.",
            "status": True,
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_201_CREATED)