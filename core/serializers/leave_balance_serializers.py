from rest_framework import serializers
from ..models.leave_balance_models import LeaveBalance
from core.utils.validator_utils import validate_leave_balance


# ==========BREAK LEAVE BALANCCE SERIALIZERS===============
class LeaveBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = ['anual_leave_balance', 'anual_leave_refresh_date', 'already_used_balance']
        extra_kwargs = {
            'anual_leave_balance': {'required': True},
            'anual_leave_refresh_date': {'required': True},
            'already_used_balance': {'required': True}
        }

    def validate(self, data):
        return validate_leave_balance(data)
