
from django.urls import path
from ..views.notification_views import (
    NotificationListAPIView,
    NotificationDetailAPIView,
    MarkAllReadAPIView,
    NotificationDeleteAPIView,
)

urlpatterns = [
    path("api/notifications/", NotificationListAPIView.as_view()),
    path("api/notifications/<uuid:pk>/", NotificationDetailAPIView.as_view()),
    path("api/notifications/mark-all-read/", MarkAllReadAPIView.as_view()),
    path("api/notifications/<uuid:pk>/delete/", NotificationDeleteAPIView.as_view()),
]
