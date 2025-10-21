from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _
import uuid
from ..models import LastLogin, User

class TokenAuthentication(BaseAuthentication):
    """
    Custom token-based authentication using the LastLogin model.
    Validates tokens and checks user activity status.
    """
    
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None  # Allow other authentication methods to try

        try:
            auth_type, token = auth_header.split(" ", 1)
        except ValueError:
            raise PermissionDenied(
                detail=_("Invalid authorization header format"),
                code="invalid_header"
            )

        if auth_type.lower() != "bearer":
            return None  # Unsupported auth type, skip this authenticator

        try:
            token_uuid = uuid.UUID(token)
        except ValueError:
            raise PermissionDenied(
                detail=_("Invalid token format"),
                code="invalid_token"
            )

        try:
            login_entry = LastLogin.objects.select_related('user').get(
                token=token_uuid,
                token_valid=True
            )
        except LastLogin.DoesNotExist:
            raise PermissionDenied(
                detail=_("Token is invalid or expired"),
                code="invalid_token"
            )

        user = login_entry.user
        if not user.is_active:
            raise PermissionDenied(
                detail=_("User account is inactive"),
                code="inactive_user"
            )

        return (user, None)  # Authentication successful