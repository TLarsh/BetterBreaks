import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
from .serializers import PaymentSerializer


class PaystackGateway:
    base_url = "https://api.paystack.co"

    @staticmethod
    def initiate_payment(booking: Booking):
        amount_kobo = int(float(booking.event.price) * 100)  # Paystack uses kobo
        url = f"{PaystackGateway.base_url}/transaction/initialize"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        data = {
            "email": booking.user.email,
            "amount": amount_kobo,
            "callback_url": settings.PAYSTACK_CALLBACK_URL,
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if response.status_code == 200 and response_data.get("status"):
            payment_data = {
                "booking_id": booking.id,
                "reference": response_data["data"]["reference"],
                "amount": booking.event.price,
                "status": "pending",
                "authorization_url": response_data["data"]["authorization_url"],
            }
            serializer = PaymentSerializer(payment_data)
            return Response({
                "message": "Payment initialized successfully.",
                "status": True,
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Payment initialization failed.",
            "status": False,
            "data": None,
            "errors": response_data.get("message", "Unknown error")
        }, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def verify_payment(reference: str, booking: Booking):
        url = f"{PaystackGateway.base_url}/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200 and response_data.get("status"):
            data = response_data["data"]
            if data["status"] == "success":
                booking.is_paid = True
                booking.save()

                payment_data = {
                    "booking_id": booking.id,
                    "reference": data["reference"],
                    "amount": booking.event.price,
                    "status": "success",
                    "authorization_url": None
                }
                serializer = PaymentSerializer(payment_data)
                return Response({
                    "message": "Payment verified successfully.",
                    "status": True,
                    "data": serializer.data,
                    "errors": None
                }, status=status.HTTP_200_OK)

        return Response({
            "message": "Payment verification failed.",
            "status": False,
            "data": None,
            "errors": response_data.get("message", "Unknown error")
        }, status=status.HTTP_400_BAD_REQUEST)
