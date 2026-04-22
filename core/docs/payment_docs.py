from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

# --- Payment Annotations ---

# initiate_payment_docs = swagger_auto_schema(
#     operation_summary="Initiate Payment",
#     operation_description="Starts a payment process for a booking using Paystack.",
#     responses={
#         200: openapi.Response(
#             description="Payment initiation successful",
#             examples={
#                 "application/json": {
#                     "message": "Payment initiated successfully",
#                     "status": True,
#                     "data": {
#                         "authorization_url": "https://checkout.paystack.com/xyz123",
#                         "access_code": "xyz123",
#                         "reference": "ref123"
#                     },
#                     "errors": None
#                 }
#             },
#         ),
#         404: openapi.Response(description="Booking not found"),
#     }
# )


# verify_payment_docs = swagger_auto_schema(
#     operation_summary="Verify Payment",
#     operation_description="Verifies a Paystack payment and updates booking/payment status.",
#     request_body=openapi.Schema(
#         type=openapi.TYPE_OBJECT,
#         properties={
#             "reference": openapi.Schema(type=openapi.TYPE_STRING, description="Paystack payment reference"),
#         },
#         required=["reference"],
#     ),
#     responses={
#         200: openapi.Response(
#             description="Payment verification successful",
#             examples={
#                 "application/json": {
#                     "message": "Payment verified successfully",
#                     "status": True,
#                     "data": {"status": "success"},
#                     "errors": None
#                 }
#             },
#         ),
#         400: openapi.Response(description="Missing or invalid reference"),
#         404: openapi.Response(description="Booking not found"),
#     }
# )






# INITIATE PAYMENT DOC
initiate_payment_docs = {
    "operation_summary": "Initialize Payment",
    "operation_description": "Initialize a payment using Paystack or Stripe",

    "request_body": openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=["booking_id", "provider"],
        properties={
            "booking_id": openapi.Schema(
                type=openapi.TYPE_INTEGER,
                example=1
            ),
            "provider": openapi.Schema(
                type=openapi.TYPE_STRING,
                enum=["PAYSTACK", "STRIPE"],
                example="STRIPE"
            ),
        },
    ),

    "responses": {
        200: openapi.Response(
            description="Payment initialized successfully",
            examples={
                "application/json": {
                    "message": "Payment initialized",
                    "status": True,
                    "data": {
                        "client_secret": "pi_xxx_secret_xxx",
                        "reference": "pi_xxx"
                    },
                    "errors": None
                }
            }
        ),
        400: openapi.Response(
            description="Initialization failed",
            examples={
                "application/json": {
                    "message": "Initialization failed",
                    "status": False,
                    "data": None,
                    "errors": {"detail": "Error message"}
                }
            }
        )
    }
}


# VERIFY PAYMENT DOC
verify_payment_docs = {
    "operation_summary": "Verify Payment",
    "operation_description": "Verify a payment using reference and provider",

    "manual_parameters": [
        openapi.Parameter(
            "reference",
            openapi.IN_QUERY,
            description="Payment reference",
            type=openapi.TYPE_STRING,
            required=True,
            example="pi_xxx"
        ),
        openapi.Parameter(
            "provider",
            openapi.IN_QUERY,
            description="Payment provider",
            type=openapi.TYPE_STRING,
            enum=["PAYSTACK", "STRIPE"],
            required=True,
            example="STRIPE"
        ),
    ],

    "responses": {
        200: openapi.Response(
            description="Payment verified successfully",
            examples={
                "application/json": {
                    "message": "Payment verified",
                    "status": True,
                    "data": None,
                    "errors": None
                }
            }
        ),
        400: openapi.Response(
            description="Verification failed",
            examples={
                "application/json": {
                    "message": "Verification failed",
                    "status": False,
                    "data": None,
                    "errors": {"detail": "Error message"}
                }
            }
        )
    }
}