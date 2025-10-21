from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..serializers.settings_serializers import (
    UserSettingsSerializer,
)
from ..models.settings_models import UserSettings

# =============USER SETTINGS=============

class UserSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: UserSettingsSerializer()},
        operation_description="Get the authenticated user's app settings"
    )
    def get(self, request):
        user = request.user
        settings_obj, _ = UserSettings.objects.get_or_create(user=user)
        serializer = UserSettingsSerializer(settings_obj)
        return Response({
            "message": "Settings retrieved successfully.",
            "status": True,
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        request_body=UserSettingsSerializer,
        responses={200: openapi.Response(description="Settings updated successfully")}
    )
    def put(self, request):
        user = request.user
        settings_obj, _ = UserSettings.objects.get_or_create(user=user)

        serializer = UserSettingsSerializer(settings_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Settings updated successfully.",
                "status": True,
                "data": None,
                "errors": None
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Validation failed.",
            "status": False,
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class GetSettingsView(APIView):
    """Retrieve user settings JSON."""
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            settings = UserSettings.objects.get(user=request.user)
            return Response(
                {"settings_json": settings.settings_json}, 
                status=status.HTTP_200_OK
            )
        except UserSettings.DoesNotExist:
            return Response(
                {"settings_json": None}, status=status.HTTP_200_OK
            )