from rest_framework import serializers
from .leave_balance_serializers import LeaveBalanceSerializer
from .preference_serializers import BreakPreferencesSerializer
from .break_serializers import BreakPlanSerializer

# ==========FIRST LOGIN SETUP SERIALIZERS===============

# class FirstLoginSetupSerializer(serializers.Serializer):
#     LeaveBalance = LeaveBalanceSerializer(required=True)
#     Preferences = BreakPreferencesSerializer(required=True)
#     BreakPlan = BreakPlanSerializer(required=False)

#     def validate(self, attrs):
#         """
#         Custom validation for the setup:
#         - Ensure BreakPlan has both startDate and endDate if provided.
#         """
#         break_plan = attrs.get("BreakPlan")
#         if break_plan:
#             if not break_plan.get("startDate") or not break_plan.get("endDate"):
#                 raise serializers.ValidationError({
#                     "BreakPlan": "Both startDate and endDate are required if BreakPlan is provided."
#                 })
#         return attrs


class FirstLoginSetupSerializer(serializers.Serializer):
    LeaveBalance = LeaveBalanceSerializer(required=True)
    BreakPreferences = BreakPreferencesSerializer(required=True)
    BreakPlan = BreakPlanSerializer(required=False)

    def validate(self, attrs):
        """
        Custom validation for setup:
        - Ensure BreakPlan has both startDate and endDate if provided.
        - Reject unexpected keys (like 'Preferences' instead of 'BreakPreferences').
        """
        # Get raw request data to compare keys
        incoming_keys = set(self.initial_data.keys())
        expected_keys = {"LeaveBalance", "BreakPreferences", "BreakPlan"}

        unexpected = incoming_keys - expected_keys
        if unexpected:
            raise serializers.ValidationError({
                "error": f"Unexpected field(s): {', '.join(unexpected)}. "
                         f"Expected only {', '.join(expected_keys)}"
            })

        # Validate BreakPlan dates
        break_plan = attrs.get("BreakPlan")
        if break_plan:
            if not break_plan.get("startDate") or not break_plan.get("endDate"):
                raise serializers.ValidationError({
                    "BreakPlan": "Both startDate and endDate are required if BreakPlan is provided."
                })

        return attrs
    
# GET and PUT action
class FirstLoginSetupDataSerializer(serializers.Serializer):
    LeaveBalance = LeaveBalanceSerializer()
    BreakPreferences = BreakPreferencesSerializer()
    BreakPlan = BreakPlanSerializer()
