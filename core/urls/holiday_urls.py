from django.urls import path
from ..views.holiday_views import HolidayView, UpcomingHolidaysView  # HolidayDetailView


urlpatterns = [
    # Holidays (APIViews replacing ViewSet)
     path('api/holidays/', HolidayView.as_view(), name='holiday-list'),
    #  path('api/holidays/<int:pk>/', HolidayDetailView.as_view(), name='holiday-detail'),
     path('api/holidays/upcoming/', UpcomingHolidaysView.as_view(), name='upcoming-holidays'),
]