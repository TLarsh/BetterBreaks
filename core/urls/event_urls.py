from django.urls import path
from ..views.event_views import (
    EventListView,
    CreateEventView,
    # BookEventView,
    # EventDetailView,
    UpdateEventView,
    DeleteEventView
)

urlpatterns = [
        path("api/events/", EventListView.as_view(), name="list_events"),
        # path("events/book", BookEventView.as_view(), name="book_event"),
        # path("events/<int:event_id>/", EventDetailView.as_view(), name="event-detail"),
        path("api/events/create/", CreateEventView.as_view(), name="create-event"),
        path("api/events/<int:event_id>/update/", UpdateEventView.as_view(), name="update-event"),
        path("api/events/<int:event_id>/delete/", DeleteEventView.as_view(), name="delete-event"),
]