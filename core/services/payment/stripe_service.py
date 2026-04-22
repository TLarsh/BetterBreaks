import stripe
from django.conf import settings
from .base_service import BasePaymentService

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService(BasePaymentService):

    def initialize_payment(self, booking, user):
        intent = stripe.PaymentIntent.create(
            amount=int(booking.total_amount * 100),
            currency="usd",
            metadata={
                "booking_id": str(booking.id),
                "user_id": str(user.id),
            }
        )

        return {
            "client_secret": intent.client_secret,
            "reference": intent.id
        }

    def verify_payment(self, reference):
        intent = stripe.PaymentIntent.retrieve(reference)
        return intent