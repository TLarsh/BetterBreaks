from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema
from ..serializers.contact_serializers import ContactMessageSerializer
from ..utils.responses import success_response, error_response


class SendMessageView(APIView):
    """Send us a message API"""
    authentication_classes = []
    permission_classes = [AllowAny]

    @swagger_auto_schema(request_body=ContactMessageSerializer)
    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Your message has been received. We’ll get back to you soon.",
                data=None,
                status_code=status.HTTP_201_CREATED
            )
        return error_response(
            message="Failed to send message.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )