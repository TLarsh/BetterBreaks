from jose import jwt
import requests
from django.conf import settings
from core.models.user_models import User

APPLE_ISSUER = "https://appleid.apple.com"
APPLE_AUDIENCE = settings.APPLE_CLIENT_ID


def verify_apple_id_token(id_token):
    try:
        headers = jwt.get_unverified_header(id_token)
        kid = headers["kid"]

        # Fetch Apple public keys
        apple_keys = requests.get(
            "https://appleid.apple.com/auth/keys"
        ).json()["keys"]

        key = next(k for k in apple_keys if k["kid"] == kid)

        payload = jwt.decode(
            id_token,
            key,
            algorithms=["RS256"],
            audience=APPLE_AUDIENCE,
            issuer=APPLE_ISSUER,
        )

        return payload

    except Exception:
        return None
    


def handle_apple_login(payload, first_name=None, last_name=None):
    email = payload.get("email")
    apple_id = payload.get("sub")

    if not apple_id:
        return None

    user = User.objects.filter(email=email).first()

    if not user:
        user = User.objects.create(
            email=email,
            full_name=f"{first_name or ''} {last_name or ''}".strip(),
            apple_id=apple_id,
        )

    return user