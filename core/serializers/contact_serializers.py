from rest_framework import serializers
from ..models.contact_message_models import ContactMessage 

####### CONTACT US #########


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ["full_name", "email", "subject", "message"]

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        return value
