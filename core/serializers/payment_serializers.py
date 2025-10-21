from rest_framework import serializers


class PaymentSerializer(serializers.Serializer):
    """
    Serializer for payment initiation and verification
    """
    booking_id = serializers.IntegerField(required=True)
    reference = serializers.CharField(read_only=True)
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    status = serializers.CharField(read_only=True)
    authorization_url = serializers.CharField(read_only=True)