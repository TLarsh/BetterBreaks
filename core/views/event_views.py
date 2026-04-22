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
from rest_framework.parsers import MultiPartParser, FormParser
from ..docs.event_docs import event_list_docs, create_event_docs, update_event_docs, partial_update_event_docs, delete_event_docs, event_detail_docs
  



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
        category = request.query_params.get("category")  # single
        categories = request.query_params.getlist("categories")  # multiple
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        min_price = request.query_params.get("min_price")
        max_price = request.query_params.get("max_price")

       
        if title:
            events = events.filter(title__icontains=title)

      
        if location:
            events = events.filter(location__icontains=location)

        
        if category:
            events = events.filter(category=category.upper())

       
        if categories:
            categories = [c.upper() for c in categories]
            events = events.filter(category__in=categories)

       
        if start_date and end_date:
            events = events.filter(
                start_date__gte=start_date,
                end_date__lte=end_date
            )

      
        if min_price and max_price:
            events = events.filter(price__gte=min_price, price__lte=max_price)
        elif min_price:
            events = events.filter(price__gte=min_price)
        elif max_price:
            events = events.filter(price__lte=max_price)

        serializer = EventSerializer(events, many=True)

        return Response({
            "message": "Events retrieved successfully",
            "status": True,
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)


# class BookEventView(APIView):
#     permission_classes = [IsAuthenticated]

#     @book_event_docs
#     def post(self, request, event_id):
#         event = get_object_or_404(Event, id=event_id)
#         booking = Booking.objects.create(user=request.user, event=event)
#         serializer = BookingSerializer(booking)

#         return Response({
#             "message": "Event booked successfully. Proceed to payment.",
#             "status": True,
#             "data": serializer.data,
#             "errors": None
#         }, status=status.HTTP_201_CREATED)
    

class CreateEventView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @create_event_docs
    def post(self, request):
        serializer = EventSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "message": "Event creation failed.",
                "status": False,
                "data": None,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        event = serializer.save()

        return Response({
            "message": "Event created successfully.",
            "status": True,
            "data": EventSerializer(event).data,
            "errors": None
        }, status=status.HTTP_201_CREATED)
    


class UpdateEventView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @update_event_docs
    def put(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        serializer = EventSerializer(event, data=request.data, partial=False)

        if not serializer.is_valid():
            return Response({
                "message": "Event update failed.",
                "status": False,
                "data": None,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            "message": "Event updated successfully.",
            "status": True,
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)
    
    @partial_update_event_docs
    def patch(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        serializer = EventSerializer(event, data=request.data, partial=True)

        if not serializer.is_valid():
            return Response({
                "message": "Partial update failed.",
                "status": False,
                "data": None,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response({
            "message": "Event partially updated successfully.",
            "status": True,
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)


class DeleteEventView(APIView):
    permission_classes = [IsAuthenticated]
    @delete_event_docs
    def delete(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        if event.created_by != request.user:
            return Response({
                "message": "Unauthorized.",
                "status": False,
                "data": None,
                "errors": {"detail": "You cannot delete this event"}
            }, status=status.HTTP_403_FORBIDDEN)

        event.delete()

        return Response({
            "message": "Event deleted successfully.",
            "status": True,
            "data": None,
            "errors": None
        }, status=status.HTTP_200_OK)
    


class EventDetailView(APIView):
    permission_classes = [AllowAny]
    @event_detail_docs
    def get(self, request, pk):
        event = get_object_or_404(Event, pk=pk)

        serializer = EventSerializer(event)

        return Response({
            "message": "Event retrieved successfully.",
            "status": True,
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)