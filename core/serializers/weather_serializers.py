from rest_framework import serializers

class WeatherForecastDaySerializer(serializers.Serializer):
    time = serializers.CharField()
    values = serializers.DictField()