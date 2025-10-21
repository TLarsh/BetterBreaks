from django.contrib import admin
from core.models.contact_message_models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "email",
        "subject",
        "message",
    )
    search_fields = ("full_name",)