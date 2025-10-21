from rest_framework import serializers
from ..models.event_models import Event
from ..models.booking_models import Booking





########################################
######Event and Booking Serializers######



class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "location",
            "start_date",
            "end_date",
            "price",
            "image",
            "created_at",
            "updated_at",
        ]


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
