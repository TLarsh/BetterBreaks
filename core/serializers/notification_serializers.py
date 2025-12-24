

from rest_framework import serializers
from ..models.notification_models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
        read_only_fields = (
            "id",
            "status",
            "sent_at",
            "created_at",
            "error_message",
            "read_at",
        )
