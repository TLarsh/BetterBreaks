from rest_framework import permissions
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import os

class SchemaGenerator(OpenAPISchemaGenerator):
  def get_schema(self, request=None, public=False):
    schema = super(SchemaGenerator, self).get_schema(request, public)
    schema.basePath = os.path.join(schema.basePath, 'v1/')
    return schema

schema_view = get_schema_view(
    openapi.Info(
        title="BetterBreaks",
        default_version='v1',
        description="BetterBreaks Backend",
        terms_of_service="https://testing.betterbreaks.org",
        contact=openapi.Contact(email="support@betterbreaks.org"),
        license=openapi.License(name="Proprietary"),
    ),
    url="https://api.betterbreaks.org/",
    public=True,
    permission_classes=(permissions.AllowAny,),
    generator_class=SchemaGenerator,
)
