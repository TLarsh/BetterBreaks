from django.urls import path
from ..views.date_views import (
    SpecialDateListCreateView,
    SpecialDateDetailView,
    AddBlackoutDateView,
    BlackoutDatesView,
    DeleteBlackoutDateView,
)

urlpatterns = [
    # path("api/suggested-dates/", SuggestedDatesView.as_view(), name="suggested-dates"),
    # path('api/dates/', DateListView.as_view(), name='dates'),       # Ensure 'dates' matches test
    # path("api/dates/add/", AddDateView.as_view(), name="add-date"),
    path("api/dates/special-dates/", SpecialDateListCreateView.as_view(), name="special-dates-list-create"),
    path("api/dates/special-dates/<uuid:pk>/", SpecialDateDetailView.as_view(), name="special-dates-detail"),
    path("api/dates/blackout-dates-add/", AddBlackoutDateView.as_view(),name="add-blackout-date"),
    path("api/dates/blackout-dates/", BlackoutDatesView.as_view(),name="blackout-dates"),
    path("api/dates/blackout-date-delete/<uuid:blackout_uuid>/", DeleteBlackoutDateView.as_view(),name="delete-blackout-date"),
]