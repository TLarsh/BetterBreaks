from django.urls import path
from ..views.payment_views import InitiatePaymentView, VerifyPaymentView  #, PaystackWebhookView

urlpatterns = [
    path("api/bookings/<int:booking_id>/payments/initiate/", InitiatePaymentView.as_view(), name="initiate-payment"),
    path("api/bookings/<int:booking_id>/payments/verify/", VerifyPaymentView.as_view(), name="verify-payment"),
    # path("api/payments/webhook/", PaystackWebhookView.as_view(), name="paystack-webhook"),

]