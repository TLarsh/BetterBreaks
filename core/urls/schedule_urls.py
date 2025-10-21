from django.urls import path
from ..views.schedule_views import ScheduleView

urlpatterns = [
    path("api/schedule", ScheduleView.as_view(), name="schedule"),
]