# from django.urls import path
# from ..views.payment_views import InitiatePaymentView, VerifyPaymentView  #, PaystackWebhookView

# urlpatterns = [
#     path("api/bookings/<int:booking_id>/payments/initiate/", InitiatePaymentView.as_view(), name="initiate-payment"),
#     path("api/bookings/<int:booking_id>/payments/verify/", VerifyPaymentView.as_view(), name="verify-payment"),
#     # path("api/payments/webhook/", PaystackWebhookView.as_view(), name="paystack-webhook"),

# ]



# urls.py

from django.urls import path
from ..views.payment_views import InitializePaymentView
from ..views.stripe_webhook_views import stripe_webhook
from ..views.payment_views import VerifyPaymentView

urlpatterns = [
    path("api/payments/stripe/initialize/", InitializePaymentView.as_view()),
    path("api/payments/stripe/verify/", VerifyPaymentView.as_view()),  # optional
    path("api/payments/stripe/webhook/", stripe_webhook),
]