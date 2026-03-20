from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from core.models.user_models import User, SocialAccount, LastLogin


def verify_google_id_token(id_token_str):
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID  # MUST be WEB client ID
        )
        return idinfo
    except Exception:
        return None
    


def handle_mobile_google_login(idinfo):
    email = idinfo.get("email")
    provider_id = idinfo.get("sub")

    if not email:
        return None

    user, _ = User.objects.get_or_create(email=email)

    # Update user info
    user.full_name = idinfo.get("name", user.full_name)
    user.profile_picture_path = idinfo.get("picture", user.profile_picture_path)
    user.save()

    SocialAccount.objects.update_or_create(
        provider="google",
        provider_id=provider_id,
        defaults={
            "user": user,
            "email": email,
            "extra_data": idinfo,
        }
    )

    return user