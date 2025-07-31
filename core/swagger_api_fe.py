# from rest_framework import permissions
# from drf_yasg.generators import OpenAPISchemaGenerator
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
# import os

# class SchemaGenerator(OpenAPISchemaGenerator):
#   def get_schema(self, request=None, public=False):
#     schema = super(SchemaGenerator, self).get_schema(request, public)
#     schema.basePath = os.path.join(schema.basePath, 'v1/')
#     return schema

# schema_view = get_schema_view(
#     openapi.Info(
#         title="BetterBreaks",
#         default_version='v1',
#         description="BetterBreaks Backend",
#         terms_of_service="https://testing.betterbreaks.org",
#         contact=openapi.Contact(email="support@betterbreaks.org"),
#         license=openapi.License(name="Proprietary"),
#     ),
#     url="https://api.betterbreaks.org/",
#     public=True,
#     permission_classes=(permissions.AllowAny,),
#     generator_class=SchemaGenerator,
# )





# swagger_api_fe.py

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# ========== Swagger Docs for GET Schedule ==========
schedule_get_schema = swagger_auto_schema(
    operation_summary="Retrieve user's full schedule",
    tags=["User Schedule"],
    responses={
        200: openapi.Response(
            description="Schedule retrieved successfully.",
        ),
        500: openapi.Response(description="Internal server error.")
    }
)

# ========== Swagger Docs for POST Schedule ==========

schedule_post_schema = swagger_auto_schema(
    operation_summary="Update user's full schedule",
    tags=["User Schedule"],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "working_pattern": openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "pattern_type": openapi.Schema(type=openapi.TYPE_STRING),
                    "days_on": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "days_off": openapi.Schema(type=openapi.TYPE_INTEGER),
                    "start_date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                    "rotation_pattern": openapi.Schema(type=openapi.TYPE_STRING),
                    "shift_preview": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING)
                        )
                    )
                }
            ),
            "blackout_dates": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "start_date": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                        "end_date": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                        "description": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            "optimization_goals": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING)
            )
        },
        required=["working_pattern"]
    ),
    responses={
        200: openapi.Response(description="Schedule updated successfully."),
        400: openapi.Response(description="Validation failed."),
        500: openapi.Response(description="Internal server error."),
    }
)






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
                        "username": "johndoe"
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
                        "username": "johndoe"
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
                        "username": "johndoe"
                    },
                    "errors": None
                }
            }
        )
    }
)