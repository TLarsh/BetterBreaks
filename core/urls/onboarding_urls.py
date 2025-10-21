from django.urls import path
from ..views.onboarding_views import FirstLoginSetupView, FirstLoginSetupUpdateView, FirstLoginSetupDataView

urlpatterns = [
    path("api/onboarding/set/", FirstLoginSetupView.as_view(), name="onboarding"),
    path("api/onboarding/setup-update/", FirstLoginSetupUpdateView.as_view(), name="first-login-setup-update"),
    path("api/onboarding/setup-data/", FirstLoginSetupDataView.as_view(), name="first-login-setup-data"),
]