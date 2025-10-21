from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# --- Payment Annotations ---

initiate_payment_docs = swagger_auto_schema(
    operation_summary="Initiate Payment",
    operation_description="Starts a payment process for a booking using Paystack.",
    responses={
        200: openapi.Response(
            description="Payment initiation successful",
            examples={
                "application/json": {
                    "message": "Payment initiated successfully",
                    "status": True,
                    "data": {
                        "authorization_url": "https://checkout.paystack.com/xyz123",
                        "access_code": "xyz123",
                        "reference": "ref123"
                    },
                    "errors": None
                }
            },
        ),
        404: openapi.Response(description="Booking not found"),
    }
)


verify_payment_docs = swagger_auto_schema(
    operation_summary="Verify Payment",
    operation_description="Verifies a Paystack payment and updates booking/payment status.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "reference": openapi.Schema(type=openapi.TYPE_STRING, description="Paystack payment reference"),
        },
        required=["reference"],
    ),
    responses={
        200: openapi.Response(
            description="Payment verification successful",
            examples={
                "application/json": {
                    "message": "Payment verified successfully",
                    "status": True,
                    "data": {"status": "success"},
                    "errors": None
                }
            },
        ),
        400: openapi.Response(description="Missing or invalid reference"),
        404: openapi.Response(description="Booking not found"),
    }
)