from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.utils.timezone import now
from ..serializers.holiday_serializers import PublicHolidaySerializer
from ..models.holiday_models import PublicHoliday, PublicHolidayCalendar
from ..docs.holiday_docs import (
    holiday_detail_get,
    # holiday_detail_post,
)
from ..utils.calendar_utils import fetch_public_holidays
from ..utils.responses import success_response, error_response
from ..tasks.holiday_tasks import sync_user_holidays


# class HolidayView(APIView):
#     permission_classes = [IsAuthenticated]
#     @swagger_auto_schema(
#         operation_summary="Get all holidays",
#         operation_description="Retrieve all public holidays for the logged-in user's holiday calendar.",
#         responses={200: PublicHolidaySerializer(many=True)},
#     )
    
#     def get(self, request):
#         """Get all holidays for the user's calendar"""
#         user = request.user
#         calendar = user.holiday_calendar
#         if not calendar:
#             return Response({"error": "No holiday calendar set up"}, status=400)
            
#         holidays = PublicHoliday.objects.filter(calendar=calendar)
#         serializer = PublicHolidaySerializer(holidays, many=True)
#         return Response(serializer.data)
    
#     def post(self, request):
#         """Create a new holiday"""
#         user = request.user
#         calendar = user.holiday_calendar
#         if not calendar:
#             return Response({"error": "No holiday calendar set up"}, status=400)
            
#         serializer = PublicHolidaySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(calendar=calendar)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class HolidayDetailView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self, pk, user):
#         try:
#             calendar = user.holiday_calendar
#             if not calendar:
#                 return None
#             return PublicHoliday.objects.get(pk=pk, calendar=calendar)
#         except PublicHoliday.DoesNotExist:
#             return None
    
#     @holiday_detail_get
#     def get(self, request, pk):
#         """Get a specific holiday"""
#         holiday = self.get_object(pk, request.user)
#         if not holiday:
#             return Response({"error": "Holiday not found"}, status=404)
#         serializer = PublicHolidaySerializer(holiday)
#         return Response(serializer.data)
    
#     @holiday_detail_put
#     def put(self, request, pk):
#         """Update a specific holiday"""
#         holiday = self.get_object(pk, request.user)
#         if not holiday:
#             return Response({"error": "Holiday not found"}, status=404)
#         serializer = PublicHolidaySerializer(holiday, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     @holiday_detail_delete
#     def delete(self, request, pk):
#         """Delete a specific holiday"""
#         holiday = self.get_object(pk, request.user)
#         if not holiday:
#             return Response({"error": "Holiday not found"}, status=404)
#         holiday.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# class UpcomingHolidaysView(APIView):
#     permission_classes = [IsAuthenticated]

#     @upcoming_holidays_get
#     def get(self, request):
#         """Get upcoming holidays for the user's country"""
#         user = request.user
#         calendar = user.holiday_calendar
#         if not calendar:
#             return Response({"error": "No holiday calendar set up"}, status=400)
            
#         today = date.today()
#         upcoming = PublicHoliday.objects.filter(
#             calendar=calendar,
#             date__gte=today
#         ).order_by('date')[:10]
        
#         serializer = PublicHolidaySerializer(upcoming, many=True)
#         return Response(serializer.data)

# class HolidayView(APIView):
#     """
#     Get all holidays for the logged-in user (current + next year).
#     Update user's holiday calendar country code.
#     """
#     permission_classes = [IsAuthenticated]

#     @holiday_detail_get
#     def get(self, request):
#         user = request.user
#         calendar = getattr(user, "holiday_calendar", None)

#         if not calendar or not calendar.is_enabled:
#             return error_response(
#                 message="No holiday calendar found",
#                 errors={"calendar": "No holiday calendar found"}
#             )

#         holidays = calendar.holidays.all().order_by("date")
#         serializer = PublicHolidaySerializer(holidays, many=True)

#         return success_response(
#             message="Fetched holidays successfully",
#             data=serializer.data
#         )

#     # @holiday_detail_post
#     def post(self, request):
#         """
#         Update the user's holiday calendar country code and sync holidays.
#         """
#         user = request.user
#         country_code = request.data.get("country_code")

#         if not country_code:
#             return error_response(
#                 message="Country code is required",
#                 errors={"country_code": "This field is required"},
#                 status_code=status.HTTP_400_BAD_REQUEST
#             )

    
#         calendar = user.get_calendar()

#         # Update country code + enable calendar
#         calendar.country_code = country_code
#         calendar.is_enabled = True
#         calendar.save(update_fields=["country_code", "is_enabled", "updated_at"])

#         # Queue the sync task
#         from .tasks import sync_user_holidays
#         task = sync_user_holidays.delay(user.id, country_code)

#         return success_response(
#             message="Holiday calendar updated successfully",
#             data={
#                 "country_code": country_code,
#                 "task_id": task.id,
#             },
#             status_code=status.HTTP_200_OK
#         )


class HolidayView(APIView):
    """
    Get all holidays for the logged-in user (current + next year).
    Update user's holiday calendar country code.
    """
    permission_classes = [IsAuthenticated]

    @holiday_detail_get
    def get(self, request):
        user = request.user
        calendar = getattr(user, "holiday_calendar", None)

        if not calendar or not calendar.is_enabled:
            return error_response(
                message="No holiday calendar found",
                errors={"calendar": "No holiday calendar found"}
            )

        holidays = calendar.holidays.all().order_by("date")
        serializer = PublicHolidaySerializer(holidays, many=True)

        return success_response(
            message="Fetched holidays successfully",
            data=serializer.data
        )

    # @holiday_detail_post
    def post(self, request):
        """
        Update the user's holiday calendar country code and sync holidays.
        """
        user = request.user
        country_code = request.data.get("country_code")

        if not country_code:
            return error_response(
                message="Country code is required",
                errors={"country_code": "This field is required"},
                status_code=status.HTTP_400_BAD_REQUEST
            )

    
        calendar = user.get_calendar()

        # Update country code + enable calendar
        calendar.country_code = country_code
        calendar.is_enabled = True
        calendar.save(update_fields=["country_code", "is_enabled", "updated_at"])

        # Queue the sync task
        task = sync_user_holidays.delay(user.id, country_code)

        return success_response(
            message="Holiday calendar updated successfully",
            data={
                "country_code": country_code,
                "task_id": task.id,
            },
            status_code=status.HTTP_200_OK
        )


class UpcomingHolidaysView(APIView):
    """
    Get upcoming holidays for the logged-in user (today + future dates).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        calendar = user.get_calendar()

        if not calendar.is_enabled:
            return error_response(
                message="Holiday calendar is disabled",
                errors={"calendar": "Holiday calendar is disabled"}
            )

        today = now().date()
        holidays = calendar.holidays.filter(date__gte=today).order_by("date")
        serializer = PublicHolidaySerializer(holidays, many=True)

        return success_response(
            message="Fetched upcoming holidays successfully",
            data=serializer.data
        )
    

     
class FetchPublicHolidaysView(APIView):
    def get(self, request):
        user = request.user
        if not user.home_location_timezone:
            return Response({"error": "User location not set"}, status=status.HTTP_400_BAD_REQUEST)

        country_code = user.home_location_timezone.split("/")[0]  # Extract country code
        year = timezone.now().year
        holidays_data = fetch_public_holidays(country_code, year)

        for holiday in holidays_data:
            PublicHoliday.objects.update_or_create(
                user=user,
                date=holiday["date"],
                defaults={"name": holiday["name"], "country_code": country_code}
            )

        return Response({"success": True}, status=status.HTTP_200_OK)
    

class ListPublicHolidaysView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        holidays = PublicHoliday.objects.filter(user=request.user)
        serializer = PublicHolidaySerializer(holidays, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

