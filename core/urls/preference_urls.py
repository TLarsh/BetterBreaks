from django.urls import path
from ..views.preference_views import NotificationPreferenceView


urlpatterns = [
    path('api/user/notification-preferences', NotificationPreferenceView.as_view()),
]