from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from ..serializers.user_serializers import RegisterSerializer
from ..models.user_models import User
from .validator_utils import validate_password

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes



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
        full_name=serializer.validated_data.get("full_name", ""),
        password=password
    )

    return user



# GENERATE VERIFICAITON LINK
def generate_verification_link(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    return f"{request.scheme}://{request.get_host()}/api/auth/verify-email/?uid={uid}&token={token}"
    # return f"{request.scheme}://{request.get_host()}/api/auth/verify-email/?uid={uid}&token={token}”
