from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        return Response({
            "success": False,
            "message": "Request failed",
            "errors": response.data
        }, status=response.status_code)

    # Unhandled exceptions ( HTML 500 fix)
    return Response({
        "success": False,
        "message": "Internal server error",
        "errors": {"detail": str(exc)}
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)