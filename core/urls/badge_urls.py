from django.urls import path
from ..views.badge_views import BadgeListCreateView, BadgeDetailView

urlpatterns = [
    # Badge endpoints
    path('api/badges/', BadgeListCreateView.as_view(), name='badges-list'),
    path('api/badges/<int:pk>/', BadgeDetailView.as_view(), name='badges-detail'),
]