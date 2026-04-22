from django.urls import path
from ..views.event_views import (
    EventListView,
    CreateEventView,
    # BookEventView,
    EventDetailView,
    UpdateEventView,
    DeleteEventView
)

urlpatterns = [
        path("api/events/", EventListView.as_view(), name="list_events"),
        # path("events/book", BookEventView.as_view(), name="book_event"),
        path("api/events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
        path("api/events/create/", CreateEventView.as_view(), name="create-event"),
        path("api/events/<int:pk>/update/", UpdateEventView.as_view(), name="update-event"),
        path("api/events/<int:pk>/delete/", DeleteEventView.as_view(), name="delete-event"),
]