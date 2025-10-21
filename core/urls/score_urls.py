from django.urls import path
from ..views.score_views import (
    ScoreSummaryView,
    StreakListCreateView,
    StreakDetailView,
    OptimizationListCreateView,
    OptimizationDetailView,
    # OptimizationCalculateView,
)


urlpatterns = [
    # Score endpoints
    path('api/score/summary/', ScoreSummaryView.as_view(), name='score-summary'),
    
    # Streak endpoints
    path('api/streaks/', StreakListCreateView.as_view(), name='streaks-list'),
    path('api/streaks/<int:pk>/', StreakDetailView.as_view(), name='streaks-detail'),

    # Optimization endpoints
    path('api/optimization/', OptimizationListCreateView.as_view(), name='optimization-list'),
    path('api/optimization/<int:pk>/', OptimizationDetailView.as_view(), name='optimization-detail'),
    # path('api/optimization/calculate/', OptimizationCalculateView.as_view(), name='optimization-calculate'),
]