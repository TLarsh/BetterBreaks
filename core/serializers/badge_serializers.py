from rest_framework import serializers
from ..models.badge_models import Badge

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'badge_type', 'description', 'requirements_met', 
                 'earned_date', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']