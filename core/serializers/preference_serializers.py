from rest_framework import serializers
from ..models.preference_models import BreakPreferences, UserNotificationPreference
from core.utils.validator_utils import validate_preferences


# ==========BREAK PREFERENCES SERIALIZERS===============
class BreakPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakPreferences
        fields = ['preference', 'weather_based_recommendation', 'to_be_confirmed']

    def validate(self, data):
        return validate_preferences(data)






# ======= USER NOTIFICATION SERILIZER ========

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNotificationPreference
        fields = [
            'breaksReminder',
            'suggestions',
            'deadlineAlerts',
            'weeklyDigest',
            'pushEnabled',
            'emailEnabled'
        ]