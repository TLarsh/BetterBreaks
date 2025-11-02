from rest_framework import serializers
from ..models.break_models import (BreakPlan, BreakSuggestion)
from ..models.leave_balance_models import LeaveBalance
from core.utils.validator_utils import validate_break_plan, validate_leave_balance
from django.utils.timezone import now
from datetime import date
import pytz

class BreakPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakPlan
        fields = '__all__'
        read_only_fields = ["user", "leave_balance"]

    def create(self, validated_data):
        user = self.context['request'].user
        leave_balance, _ = LeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                "anual_leave_balance": 60,
                "anual_leave_refresh_date": date.today().replace(year=date.today().year + 1),
                "already_used_balance": 0,
            }
        )
        validated_data['user'] = user
        validated_data['leave_balance'] = leave_balance
        return super().create(validated_data)




# ==========BREAK LIST SERIALIZERS===============
class BreakPlanListSerializer(serializers.ModelSerializer):
    daysCount = serializers.SerializerMethodField()
    daysRemaining = serializers.SerializerMethodField()

    class Meta:
        model = BreakPlan
        fields = [
            "id", "startDate", "endDate", "description", "type", "status",
            "daysCount", "daysRemaining", "created_at", "updated_at"
        ]

    def get_daysCount(self, obj):
        try:
            return (obj.endDate.date() - obj.startDate.date()).days + 1
        except Exception:
            return 0

    def get_daysRemaining(self, obj):
        try:
            today = date.today()
            return max((obj.endDate.date() - today).days, 0)
        except Exception:
            return 0


# ------------------

class UpcomingBreakPlanSerializer(serializers.ModelSerializer):
    days = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    starts_in = serializers.SerializerMethodField()
    local_start_date = serializers.SerializerMethodField()

    class Meta:
        model = BreakPlan
        fields = [
            "id",
            "description",
            "type",
            "status",
            "status_display",
            "startDate",
            "endDate",
            "days",
            "starts_in",
            "local_start_date",
        ]

    def get_days(self, obj):
        return (obj.endDate.date() - obj.startDate.date()).days + 1

    def get_starts_in(self, obj):
        today = now().date()
        diff = (obj.startDate.date() - today).days
        return f"In {diff} days" if diff >= 0 else "Started already"

    def get_local_start_date(self, obj):
        user = obj.user
        if not user.home_location_timezone:
            return obj.startDate.date()

        try:
            tz = pytz.timezone(user.home_location_timezone)
            local_dt = obj.startDate.astimezone(tz)
            return local_dt.strftime("%B %d")  # Example: "April 24"
        except Exception:
            return obj.startDate.date()


# ==========BREAK SUGGESTION SERIALIZERS===============
class BreakSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakSuggestion
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'reason', 'priority',
                 'is_accepted', 'based_on_mood', 'based_on_workload', 'based_on_preferences',
                 'based_on_weather', 'created_at']
        read_only_fields = ['id', 'created_at']


# ==========BREAK PLAN UPDATE SERIALIZERS===============
class BreakPlanUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakPlan
        fields = ["startDate", "endDate", "description", "status"]

    def validate(self, data):
        return validate_break_plan(data)

class BreakPlanActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=['approve', 'reject', 'take', 'miss', 'cancel', 'accept'])
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_action(self, value):
        break_plan = self.context.get('break_plan')
        # If break_plan is None, it's a suggestion, allow only 'accept'
        if not break_plan:
            if value != 'accept':
                raise serializers.ValidationError("Only 'accept' action is allowed for suggestions.")
            return value

        current_status = break_plan.status
        valid_transitions = {
            'planned': ['approve', 'reject', 'cancel'],
            'pending': ['approve', 'reject', 'cancel'],
            'approved': ['take', 'miss', 'cancel'],
            'rejected': [],
            'taken': [],
            'missed': [],
            'cancelled': [],
        }
        if value not in valid_transitions.get(current_status, []):
            raise serializers.ValidationError(
                f"Cannot perform '{value}' action on a break with '{current_status}' status"
            )
        return value
    


class BreakRecommendationSerializer(serializers.Serializer):
    work_hours_per_week = serializers.IntegerField(required=True)
    stress_level = serializers.IntegerField(required=True)
    sleep_quality = serializers.IntegerField(required=True)
    prefers_travel = serializers.BooleanField(required=True)
    season_preference = serializers.CharField(required=False, allow_blank=True)
