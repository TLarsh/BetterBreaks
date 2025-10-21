from django.urls import path
from ..views.break_views import (
    CreateBreakPlanView,
    UpcomingBreaksView,
    ListUserBreakPlansView,
    UpdateBreakPlanView,
    DeleteBreakPlanView,
    BreakPlanActionView,
    BreakLogListCreateView, BreakLogDetailView,
)

urlpatterns = [
    # Break logs endpoints
    path('api/breaks/logs/', BreakLogListCreateView.as_view(), name='break-logs-list'),
    path('api/breaks/logs/<int:pk>/', BreakLogDetailView.as_view(), name='break-logs-detail'),

    path("api/breaks/plan", CreateBreakPlanView.as_view(), name="create-break-plan"),
    path("api/breaks/upcoming", UpcomingBreaksView.as_view(), name="create-break-plan"),
    path("api/breaks/plans", ListUserBreakPlansView.as_view(), name="list-break-plans"),
    # path("api/breaks/plans/<uuid:planId>", UpdateBreakPlanView.as_view(), name="update-break-plan"),
    path("api/breaks/plan/<uuid:planId>", DeleteBreakPlanView.as_view(), name="delete-break-plan"),
    path("api/breaks/plan/action/<uuid:pk>/", BreakPlanActionView.as_view(), name="break-plan-action"),
    # path("api/breaks/suggest", BreakSuggestionListCreateView.as_view(), name="list-create-break-suggestions"),
    # path("api/breaks/suggest/<uuid:pk>", BreakSuggestionDetailView.as_view(), name="break-suggestion-detail"),
]