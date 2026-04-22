from .paystack_service import PaystackService
from .stripe_service import StripeService


class PaymentFactory:

    @staticmethod
    def get_service(provider):
        if provider == "PAYSTACK":
            return PaystackService()
        elif provider == "STRIPE":
            return StripeService()
        else:
            raise ValueError("Invalid payment provider")