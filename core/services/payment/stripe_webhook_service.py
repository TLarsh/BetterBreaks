from ...models.booking_models import Booking
from ...models.payment_models import Payment



def handle_success(intent):
    booking_id = intent["metadata"]["booking_id"]

    booking = Booking.objects.get(id=booking_id)

    # prevent duplicate processing
    if booking.status == "PAID":
        return

    booking.status = "PAID"
    booking.save()

    Payment.objects.create(
        booking=booking,
        reference=intent["id"],
        amount=booking.total_amount,
        status="SUCCESS"
    )


def handle_failed(intent):
    booking_id = intent["metadata"]["booking_id"]

    booking = Booking.objects.get(id=booking_id)
    booking.status = "FAILED"
    booking.save()