from rest_framework import serializers


class ActionLogSerializer(serializers.Serializer):
    """
    Serializer for logging application actions.
    """
    application_area_name = serializers.CharField()
    action_description = serializers.CharField()
    action_duration_seconds = serializers.IntegerField()
    token = serializers.UUIDField(required=False)  # Optional user token

    def validate_action_duration_seconds(self, value):
        if value < 0:
            raise serializers.ValidationError("Duration cannot be negative")
        return value