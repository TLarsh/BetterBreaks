from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
# from ..models.booking_models import Booking
# from ..utils.payment_gateways import PaystackGateway
from ..docs.payment_docs import initiate_payment_docs, verify_payment_docs


from ..services.payment_service import PaymentService

class InitializePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    @swagger_auto_schema(**initiate_payment_docs)
    def post(self, request):
        booking_id = request.data.get("booking_id")
        provider = request.data.get("provider")  # PAYSTACK or STRIPE

        try:
            data = PaymentService.initialize_payment(
                booking_id, request.user, provider
            )

            return Response({
                "message": "Payment initialized",
                "status": True,
                "data": data,
                "errors": None
            })

        except Exception as e:
            return Response({
                "message": "Initialization failed",
                "status": False,
                "data": None,
                "errors": {"detail": str(e)}
            }, status=400)
        

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(**verify_payment_docs)
    def get(self, request):
        reference = request.query_params.get("reference")
        provider = request.query_params.get("provider")

        try:
            PaymentService.verify_payment(reference, provider)

            return Response({
                "message": "Payment verified",
                "status": True,
                "data": None,
                "errors": None
            })

        except Exception as e:
            return Response({
                "message": "Verification failed",
                "status": False,
                "data": None,
                "errors": {"detail": str(e)}
            }, status=400)

# class InitiatePaymentView(APIView):
#     permission_classes = [IsAuthenticated]

#     @initiate_payment_docs
#     def post(self, request, booking_id):
#         try:
#             booking = Booking.objects.get(id=booking_id, user=request.user)
#         except Booking.DoesNotExist:
#             return Response({
#                 "message": "Booking not found.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"booking_id": "Invalid or unauthorized booking"}
#             }, status=404)

#         return PaystackGateway.initiate_payment(booking)


# class VerifyPaymentView(APIView):
#     permission_classes = [IsAuthenticated]

#     @verify_payment_docs
#     def post(self, request, booking_id):
#         reference = request.data.get("reference")
#         if not reference:
#             return Response({
#                 "message": "Payment reference is required.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"reference": "This field is required"}
#             }, status=400)

#         try:
#             booking = Booking.objects.get(id=booking_id, user=request.user)
#         except Booking.DoesNotExist:
#             return Response({
#                 "message": "Booking not found.",
#                 "status": False,
#                 "data": None,
#                 "errors": {"booking_id": "Invalid or unauthorized booking"}
#             }, status=404)

#         return PaystackGateway.verify_payment(reference, booking)

