from rest_framework.permissions import AllowAny
from rest_framework import status
from dj_rest_auth.registration.views import SocialLoginView
from ..models import LastLogin
from ..utils.responses import success_response, error_response
import traceback


class BaseSocialLoginView(SocialLoginView):
    """
    Base class for social logins (Google, Facebook, Twitter).
    Supports both:
    - Code-based login (requires callback_url)
    - Token-based login (no callback_url required)
    Also logs last login like LoginView.
    """

    permission_classes = [AllowAny]
    callback_url = None  # Will be set dynamically if needed

    def get_callback_url(self):
        """
        Decide whether to use callback_url.
        - If request.data has 'code' (OAuth code flow), use callback_url for Swagger UI testing.
        - If request.data has 'access_token', skip callback_url (mobile token login).
        """
        if "code" in self.request.data:
            # This should match the redirect URI you registered in provider dashboard
            return "https://localhost/auth/social/callback/"
        return None

    def post(self, request, *args, **kwargs):
        try:
            # Dynamically set callback_url before super().post()
            self.callback_url = self.get_callback_url()

            response = super().post(request, *args, **kwargs)

            if response.status_code == 200:
                user = self.user
                tokens = user.tokens()

                # Track last login like LoginView
                LastLogin.objects.create(
                    user=user,
                    client=user,
                    ip_address=request.META.get("REMOTE_ADDR", ""),
                    token=tokens["access"],
                    token_valid=True,
                )

                return success_response(
                    message="Social login successful",
                    data={
                        "refresh": tokens["refresh"],
                        "access": tokens["access"],
                        "email": user.email,
                        "full_name": user.full_name,
                        "provider": self.adapter_class.provider_id
                    }
                )

            return error_response(
                message="Social login failed",
                errors=response.data
            )

        except Exception as e:
            return error_response(
                message="An unexpected error occurred.",
                errors={"non_field_errors": [str(e), traceback.format_exc()]},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
