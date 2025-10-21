from rest_framework import serializers
from ..models.settings_models import UserSettings
import pytz 

# ==========USER SETTINGS SERIALIZERS===============

class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSettings
        fields = ['theme', 'language', 'timezone', 'currency']

    def validate_theme(self, value):
        allowed = ['light', 'dark', 'system']
        if value not in allowed:
            raise serializers.ValidationError(f"Theme must be one of {allowed}")
        return value
    def validate_timezone(self, value):
        if value not in pytz.all_timezones:
            raise serializers.ValidationError("Invalid timezone")
        return value