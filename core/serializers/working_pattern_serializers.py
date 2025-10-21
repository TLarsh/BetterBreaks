from rest_framework import serializers
from ..models.working_pattern_models import WorkingPattern

class WorkingPatternSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingPattern
        fields = '__all__'
        read_only_fields = ['user', 'created_at']