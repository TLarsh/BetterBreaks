from django.urls import path
from ..views.event_views import (
    EventListView,
    # BookEventView,
    # EventDetailView,
    CreateEventView,
    # EventUpdateView,
    # EventDeleteView
)

urlpatterns = [
        path("api/events/", EventListView.as_view(), name="list_events"),
        # path("events/book", BookEventView.as_view(), name="book_event"),
        # path("events/<int:event_id>/", EventDetailView.as_view(), name="event-detail"),
        # path("api/events/create/", CreateEventView.as_view(), name="create-event"),
        # path("events/<int:event_id>/update/", EventUpdateView.as_view(), name="update-event"),
        # path("events/<int:event_id>/delete/", EventDeleteView.as
]