from django.contrib import admin
from django.urls import include, path
from core.views.swagger_schema_ui_views import schema_view




urlpatterns = [
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('', include('core.urls.user_urls')),
    path('', include('core.urls.badge_urls')),
    path('', include('core.urls.break_urls')),
    path('', include('core.urls.contact_urls')),
    path('', include('core.urls.date_urls')),
    path('', include('core.urls.event_urls')),
    path('', include('core.urls.holiday_urls')),
    path('', include('core.urls.mood_urls')),
    path('', include('core.urls.onboarding_urls')),
    path('', include('core.urls.payment_urls')),
    path('', include('core.urls.preference_urls')),
    path('', include('core.urls.schedule_urls')),
    path('', include('core.urls.score_urls')),
    path('', include('core.urls.settings_urls')),
    path('', include('core.urls.weather_urls')),
    # path('', include('core.urls.break_recomendation_urls')),
      # Include core app URLs
]