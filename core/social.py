import requests
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema

from .utils import success_response, error_response
from .models import SocialAccount, LastLogin
from .serializers import (
    GoogleLoginSerializer,
    TwitterLoginSerializer,
    AppleLoginSerializer,
)

User = get_user_model()


class GoogleLoginView(APIView):
    """Handle Google OAuth login"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=GoogleLoginSerializer,
        responses={200: "Returns access/refresh tokens and user info"},
        operation_summary="Google OAuth Login",
        operation_description="Log in with Google ID token and receive JWT tokens.",
    )
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]

        # Verify token with Google
        google_url = "https://www.googleapis.com/oauth2/v3/tokeninfo"
        resp = requests.get(google_url, params={"id_token": token})
        if resp.status_code != 200:
            return error_response("Invalid Google token")

        data = resp.json()
        email = data.get("email")
        provider_id = data.get("sub")

        if not email:
            return error_response("Google account email not available")

        # Find or create user
        user, _ = User.objects.get_or_create(
            email=email, defaults={"username": email.split("@")[0]}
        )

        # Link or update social account
        social, _ = SocialAccount.objects.get_or_create(
            provider="google",
            provider_id=provider_id,
            user=user,
            defaults={"email": email},
        )
        social.last_login = timezone.now()
        social.save()

        # Track login
        tokens = user.tokens()
        LastLogin.objects.create(
            user=user,
            client="google",
            ip_address=request.META.get("REMOTE_ADDR", ""),
            token=tokens["access"],
            token_valid=True,
        )

        return success_response(
            "Google login successful",
            data={
                "refresh": tokens["refresh"],
                "access": tokens["access"],
                "email": user.email,
                "username": user.username,
                "provider": "google",
            },
        )


class TwitterLoginView(APIView):
    """Handle Twitter OAuth login"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=TwitterLoginSerializer,
        responses={200: "Returns access/refresh tokens and user info"},
        operation_summary="Twitter OAuth Login",
        operation_description="Log in with Twitter provider_id and optional email.",
    )
    def post(self, request):
        serializer = TwitterLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider_id = serializer.validated_data["provider_id"]
        email = serializer.validated_data.get("email")

        # Find or create user
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={"username": email.split("@")[0] if email else f"tw_{provider_id}"},
        )

        # Link or update social account
        social, _ = SocialAccount.objects.get_or_create(
            provider="twitter",
            provider_id=provider_id,
            user=user,
            defaults={"email": email},
        )
        social.last_login = timezone.now()
        social.save()

        # Track login
        tokens = user.tokens()
        LastLogin.objects.create(
            user=user,
            client="twitter",
            ip_address=request.META.get("REMOTE_ADDR", ""),
            token=tokens["access"],
            token_valid=True,
        )

        return success_response(
            "Twitter login successful",
            data={
                "refresh": tokens["refresh"],
                "access": tokens["access"],
                "email": user.email,
                "username": user.username,
                "provider": "twitter",
            },
        )


class AppleLoginView(APIView):
    """Handle Apple OAuth login"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=AppleLoginSerializer,
        responses={200: "Returns access/refresh tokens and user info"},
        operation_summary="Apple OAuth Login",
        operation_description="Log in with Apple provider_id and optional email.",
    )
    def post(self, request):
        serializer = AppleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider_id = serializer.validated_data["provider_id"]
        email = serializer.validated_data.get("email")

        # Find or create user
        user, _ = User.objects.get_or_create(
            email=email,
            defaults={
                "username": email.split("@")[0] if email else f"apple_{provider_id}"
            },
        )

        # Link or update social account
        social, _ = SocialAccount.objects.get_or_create(
            provider="apple",
            provider_id=provider_id,
            user=user,
            defaults={"email": email},
        )
        social.last_login = timezone.now()
        social.save()

        # Track login
        tokens = user.tokens()
        LastLogin.objects.create(
            user=user,
            client="apple",
            ip_address=request.META.get("REMOTE_ADDR", ""),
            token=tokens["access"],
            token_valid=True,
        )

        return success_response(
            "Apple login successful",
            data={
                "refresh": tokens["refresh"],
                "access": tokens["access"],
                "email": user.email,
                "username": user.username,
                "provider": "apple",
            },
        )
 
