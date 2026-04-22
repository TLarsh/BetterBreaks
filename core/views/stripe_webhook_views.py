import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from ..services.payment.stripe_webhook_service import (
    handle_success,
    handle_failed
)

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    # 🔥 Handle Events
    if event["type"] == "payment_intent.succeeded":
        handle_success(event["data"]["object"])

    elif event["type"] == "payment_intent.payment_failed":
        handle_failed(event["data"]["object"])

    return HttpResponse(status=200)