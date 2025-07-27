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