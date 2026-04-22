from django.shortcuts import get_object_or_404
from ..models.booking_models import Booking
from ..models.payment_models import Payment
from .payment.factory_service import PaymentFactory



class PaymentService:


    @staticmethod
    def initialize_payment(booking_id, user, provider):
        booking = get_object_or_404(Booking, id=booking_id)

        service = PaymentFactory.get_service(provider)
        response = service.initialize_payment(booking, user)

        return response

    @staticmethod
    def verify_payment(reference, provider):
        service = PaymentFactory.get_service(provider)
        response = service.verify_payment(reference)

        # Handle Paystack
        if provider == "PAYSTACK":
            if response["data"]["status"] == "success":
                booking_id = response["data"]["reference"]
                booking = Booking.objects.get(id=booking_id)

                booking.status = "PAID"
                booking.save()

                Payment.objects.create(
                    booking=booking,
                    reference=reference,
                    amount=booking.total_amount,
                    status="SUCCESS"
                )

        # Handle Stripe
        elif provider == "STRIPE":
            if response.status == "succeeded":
                booking_id = response.metadata["booking_id"]
                booking = Booking.objects.get(id=booking_id)

                booking.status = "PAID"
                booking.save()

                Payment.objects.create(
                    booking=booking,
                    reference=reference,
                    amount=booking.total_amount,
                    status="SUCCESS"
                )

        return response