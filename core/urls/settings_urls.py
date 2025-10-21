from django.urls import path
from ..views.settings_views import UserSettingsView, GetSettingsView

urlpatterns = [
path("api/user/settings", UserSettingsView.as_view(), name="user_settings"),
path('api/settings/', GetSettingsView.as_view(), name='get_settings'),
]