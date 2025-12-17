from django.urls import path
from ..views.recommendation_views import (
    UserMetricsView,
    BreakRecommendationView,
    BreakRecommendationDetailView,
    convert_to_break_plan,
)

urlpatterns = [
    path('api/user-metrics/', UserMetricsView.as_view(), name='user-metrics'),
    path('api/recommendations/', BreakRecommendationView.as_view(), name='break-recommendations'),
    path('api/recommendations/<uuid:pk>/', BreakRecommendationDetailView.as_view(), name='break-recommendation-detail'),
    path('api/recommendations/<uuid:pk>/convert/', convert_to_break_plan, name='convert-to-break-plan'),
]