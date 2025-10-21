from rest_framework import serializers
from ..models.holiday_models import PublicHoliday

class PublicHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicHoliday
        fields = ["id", "name", "date", "country_code"]