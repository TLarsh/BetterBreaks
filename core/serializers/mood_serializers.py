from rest_framework import serializers
from ..models.mood_models import Mood



# ======= Mood-SERILIZER ========
class MoodCheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ["mood_type", "note"]

class MoodHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ["mood_type", "note", "created_at"]