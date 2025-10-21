from rest_framework import serializers
from ..models.date_models import DateEntry, SpecialDate, BlackoutDate

######## DATE ENTRY ##########

class DateEntrySerializer(serializers.ModelSerializer):
    # uuid = serializers.UUIDField(source="id")  # Include UUID in response
    optimisation_score = serializers.FloatField()

    class Meta:
        model = DateEntry
        fields = ["start_date", "end_date", "title", "description", "optimisation_score"]
        # fields = ["uuid", "start_date", "end_date", "title", "description", "optimisation_score"]


# ======= SPECIAL-DATE-SERILIZER ========
class SpecialDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecialDate
        fields = ["id", "title", "date", "description", "created_at", "updated_at"]
        extra_kwargs = {
            "title": {"required": True},
            "date": {"required": True},
            "description": {"required": False},
        }


# ======= DECOY-BLACKOUT-DATE-LIST-SERILIZER ========
class BlackoutDateSerializer(serializers.ModelSerializer):
    """
    Serializer for blackout dates.
    """
    class Meta:
        model = BlackoutDate
        fields = "__all__"

# ======= BLACKOUT-DATE-LIST-SERILIZER ========
class BlackOutDateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        user = self.context['request'].user
        for item in validated_data:
            item['user'] = user
        return super().create(validated_data)

# ======= BLACKOUT-DATE-SERILIZER ========
class BlackOutDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlackoutDate
        fields = '__all__'
        read_only_fields = ('user',)
        list_serializer_class = BlackOutDateListSerializer
