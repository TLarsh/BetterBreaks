import requests
from django.conf import settings
from .base_service import BasePaymentService


class PaystackService(BasePaymentService):

    def initialize_payment(self, booking, user):
        url = "https://api.paystack.co/transaction/initialize"

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "email": user.email,
            "amount": int(booking.total_amount * 100),
            "reference": str(booking.id),
        }

        response = requests.post(url, json=data, headers=headers)
        return response.json()

    def verify_payment(self, reference):
        url = f"https://api.paystack.co/transaction/verify/{reference}"

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }

        response = requests.get(url, headers=headers)
        return response.json()