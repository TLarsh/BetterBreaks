
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
schema_view = get_schema_view(
    openapi.Info(
        title="BetterBreaks",
        default_version='v1',
        description="BetterBreaks Backend",
        terms_of_service="https://testing.betterbreaks.org",
        contact=openapi.Contact(email="support@betterbreaks.org"),
        license=openapi.License(name="Proprietary"),
    ),
    
    public=True,
    # url="http://127.0.0.1:8000//",
    permission_classes=(permissions.AllowAny,),
)