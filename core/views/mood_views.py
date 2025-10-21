from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.dateparse import parse_date
from ..serializers.mood_serializers import (
    MoodCheckInSerializer,
    MoodHistorySerializer
)
from ..models.mood_models import Mood
from ..utils.responses import success_response, error_response
from ..docs.mood_docs import (
    mood_checkin_schema,
    mood_history_schema
)



######### MOOD CHECKIN ############
class MoodCheckInView(APIView):
    permission_classes = [IsAuthenticated]
    @mood_checkin_schema
    def post(self, request):
        serializer = MoodCheckInSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "message": "Mood check-in successful",
                "status": True,
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_201_CREATED)
        return Response({
            "message": "Validation error",
            "status": False,
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class MoodHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    @mood_history_schema
    def get(self, request):
        start_date_str = request.query_params.get("start_date")
        end_date_str = request.query_params.get("end_date")

        moods = Mood.objects.filter(user=request.user)

        if start_date_str:
            start_date = parse_date(start_date_str)
            if start_date:
                moods = moods.filter(created_at__date__gte=start_date)

        if end_date_str:
            end_date = parse_date(end_date_str)
            if end_date:
                moods = moods.filter(created_at__date__lte=end_date)

        serializer = MoodHistorySerializer(moods, many=True)
        return Response({
            "message": "Mood history retrieved successfully",
            "status": True,
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)