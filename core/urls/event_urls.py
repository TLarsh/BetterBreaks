from django.urls import path
from ..views.event_views import (
    EventListView,
    BookEventView,
    # EventDetailView,
    # EventCreateView,
    # EventUpdateView,
    # EventDeleteView
)

urlpatterns = [
        # path("events/", EventListView.as_view(), name="list_events"),
        # path("events/<int:event_id>/", EventDetailView.as_view(), name="event-detail"),
        # path("events/create/", EventCreateView.as_view(), name="create-event"),
        # path("events/<int:event_id>/update/", EventUpdateView.as_view(), name="update-event"),
        # path("events/<int:event_id>/delete/", EventDeleteView.as
]