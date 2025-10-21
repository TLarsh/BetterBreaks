from django.urls import path
from ..views.mood_views import MoodCheckInView, MoodHistoryView

urlpatterns = [
    path(
        "api/moods/checkin/",
        MoodCheckInView.as_view(),
        name='mood-checkin'
    ),
    path(
        "api/moods/history/",
        MoodHistoryView.as_view(),
        name='mood-history'
    ),
]