from django.contrib import admin
from core.models.leave_balance_models import LeaveBalance

# custom admin configuration for LeaveBalance Model
@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("anual_leave_balance", "already_used_balance", "anual_leave_refresh_date", "updated_at")
    readonly_fields = ("updated_at",)
    search_fields = ("anual_leave_balance",)