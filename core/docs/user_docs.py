from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



# ----------- GOOGLE LOGIN SCHEMA -----------
google_login_schema = swagger_auto_schema(
    operation_summary="Login with Google",
    operation_description=(
        "Authenticate a user using Google OAuth.\n"
        "- Provide either the `access_token` (from Google) or the `code` (OAuth authorization code).\n"
        "- The callback URL must match the one configured in Google Cloud Console."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Google OAuth access token"),
            "code": openapi.Schema(type=openapi.TYPE_STRING, description="Google OAuth authorization code"),
        },
        example={
            "access_token": "ya29.a0AfH6SMBEXAMPLE...",
            "code": "4/0AX4XfWhExampleCodeFromGoogle"
        }
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "status": True,
                    "data": {
                        "refresh": "your_refresh_token",
                        "access": "your_access_token",
                        "email": "user@example.com",
                        "full_name": "John Doe"
                    },
                    "errors": None
                }
            }
        )
    }
)

# ----------- FACEBOOK LOGIN SCHEMA -----------
facebook_login_schema = swagger_auto_schema(
    operation_summary="Login with Facebook",
    operation_description=(
        "Authenticate a user using Facebook OAuth.\n"
        "- Provide the `access_token` obtained from Facebook's OAuth flow.\n"
        "- The callback URL must match the one configured in Facebook Developer Dashboard."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Facebook OAuth access token"),
        },
        example={
            "access_token": "EAAJZCwExampleFacebookToken"
        }
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "status": True,
                    "data": {
                        "refresh": "your_refresh_token",
                        "access": "your_access_token",
                        "email": "user@example.com",
                        "full_name": "John Doe"
                    },
                    "errors": None
                }
            }
        )
    }
)

# ----------- TWITTER LOGIN SCHEMA -----------
twitter_login_schema = swagger_auto_schema(
    operation_summary="Login with Twitter",
    operation_description=(
        "Authenticate a user using Twitter OAuth.\n"
        "- For OAuth 1.0a: Provide `access_token` and `access_token_secret`.\n"
        "- For OAuth 2.0: Provide the `code` from Twitter's OAuth flow."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "access_token": openapi.Schema(type=openapi.TYPE_STRING, description="Twitter OAuth access token"),
            "access_token_secret": openapi.Schema(type=openapi.TYPE_STRING, description="Twitter OAuth token secret (OAuth 1.0a only)"),
            "code": openapi.Schema(type=openapi.TYPE_STRING, description="Twitter OAuth authorization code (OAuth 2.0 only)"),
        },
        example={
            "access_token": "ExampleTwitterAccessToken",
            "access_token_secret": "ExampleTwitterTokenSecret",
            "code": "ExampleTwitterOAuthCode"
        }
    ),
    responses={
        200: openapi.Response(
            description="Login successful",
            examples={
                "application/json": {
                    "message": "Login successful",
                    "status": True,
                    "data": {
                        "refresh": "your_refresh_token",
                        "access": "your_access_token",
                        "email": "user@example.com",
                        "full_name": "John Doe"
                    },
                    "errors": None
                }
            }
        )
    }
)
