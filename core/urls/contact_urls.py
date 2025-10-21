from django.urls import path
from ..views.contact_views import SendMessageView



urlpatterns = [
        path("api/message/send/", SendMessageView.as_view(), name="send-message"),
]