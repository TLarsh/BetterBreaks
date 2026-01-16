# views/notification_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from ..models.notification_models import Notification
from ..services.notification_service import NotificationCRUDService
from ..serializers.notification_serializers import NotificationSerializer


class NotificationListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = NotificationCRUDService.list_for_user(request.user)
        return Response(NotificationSerializer(qs, many=True).data)


class NotificationDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        notification = NotificationCRUDService.get_and_mark_read(
            request.user, pk
        )
        return Response(NotificationSerializer(notification).data)


class MarkAllReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        NotificationCRUDService.mark_all_read(request.user)
        return Response({"message": "All notifications marked as read"})


class NotificationDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        NotificationCRUDService.delete(request.user, pk)
        return Response(status=204)



class UnreadNotificationCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            user=request.user,
            channel="system",
            is_read=False,
        ).count()

        return Response({
            "message": "Unread notifications count",
            "status": True,
            "data": {"unread_count": count},
            "errors": None,
        })
