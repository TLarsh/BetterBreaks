from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers, status
from .serializers import RegisterSerializer
from .models import User
from .validators import validate_password



def validate_and_create_user(data):
    """
    Validates registration data and creates a user.
    Raises serializers.ValidationError or DjangoValidationError on failure.
    """

    serializer = RegisterSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    # Check password match
    password = serializer.validated_data.get("password")
    password_confirmation = serializer.validated_data.get("password_confirmation")

    if password != password_confirmation:
        raise serializers.ValidationError({"errors": ["Passwords do not match"]})

    # Validate password rules
    try:
        validate_password(password)
    except DjangoValidationError as e:
        raise serializers.ValidationError({"errors": e.messages})

    # Create user
    user = User.objects.create_user(
        email=serializer.validated_data["email"],
        username=serializer.validated_data.get("username", ""),
        password=password
    )

    return user
