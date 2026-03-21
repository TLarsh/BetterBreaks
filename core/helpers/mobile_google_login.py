from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.conf import settings
from core.models.user_models import User, SocialAccount, LastLogin


def verify_google_id_token(id_token_str):
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),  # ensure correct request
            settings.GOOGLE_CLIENT_ID
        )
        print("✅ Verified! ID info:", idinfo)
        return idinfo
    except ValueError as e:
        print("❌ Verification failed:", e)
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



import base64
import json
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings

def debug_google_id_token(id_token_str):
    print("\n=== Received ID Token ===")
    print(id_token_str)

    # Step 1: Decode payload without verification
    try:
        payload_b64 = id_token_str.split('.')[1] + '=='
        decoded = json.loads(base64.urlsafe_b64decode(payload_b64))
        print("\n=== Decoded Token Payload ===")
        print(json.dumps(decoded, indent=2))
    except Exception as e:
        print("❌ Failed to decode token payload:", str(e))
        return None

    # Step 2: Verify with google-auth
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            settings.GOOGLE_CLIENT_ID  # MUST be your web client ID
        )
        print("\n✅ Token verified successfully!")
        print(json.dumps(idinfo, indent=2))
        return idinfo
    except ValueError as e:
        print("\n❌ Verification failed:", str(e))
        return None
    except Exception as e:
        print("\n❌ Unexpected error during verification:", str(e))
        return None