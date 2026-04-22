from altair import value
from rest_framework import serializers
from ..models.event_models import Event
from ..models.booking_models import Booking





########################################
######Event and Booking Serializers######



class EventSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    category_display = serializers.CharField(
        source="get_category_display",
        read_only=True
    )

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "location",
            "category",
            "category_display",
            "start_date",
            "end_date",
            "price",
            "capacity",
            "image",
            "created_at",
            "updated_at",
        ]

        def validate_category(self, value):
            valid_choices = [choice[0] for choice in Event.CategoryChoices.choices]
            if value not in valid_choices:
                raise serializers.ValidationError("Invalid category")
            return value


class BookingSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "event",
            "user",
            "is_paid",
            "created_at",
        ]
        read_only_fields = ["user", "is_paid", "created_at"]
