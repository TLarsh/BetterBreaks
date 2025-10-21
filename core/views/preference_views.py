from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers.preference_serializers import (

    NotificationPreferenceSerializer
)
from ..models.preference_models import UserNotificationPreference



#  ======== USER NOTIFICATION API VIEW ========
class NotificationPreferenceView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: NotificationPreferenceSerializer})
    def get(self, request):
        user = request.user
        preferences, created = UserNotificationPreference.objects.get_or_create(user=user)
        serializer = NotificationPreferenceSerializer(preferences)

        return Response({
            "success": True,
            "preferences": serializer.data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(request_body=NotificationPreferenceSerializer)
    def put(self, request):
        user = request.user
        preferences, _ = UserNotificationPreference.objects.get_or_create(user=user)
        serializer = NotificationPreferenceSerializer(preferences, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Notification preferences updated successfully"
            }, status=status.HTTP_200_OK)

        return Response({
            "success": False,
            "message": "Validation failed",
            "errors": serializer.errors,
            "data": None
        }, status=status.HTTP_400_BAD_REQUEST)