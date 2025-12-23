from typing import Tuple, Dict, Any, Optional
import logging
from datetime import datetime, time

from django.db import transaction
from rest_framework import serializers

from core.models.break_models import BreakPlan, BreakSuggestion
from core.models.leave_balance_models import LeaveBalance
from core.serializers.break_serializers import BreakPlanActionSerializer
from core.services.break_execution_service import BreakExecutionService

logger = logging.getLogger(__name__)


class BreakPlanService:
    @classmethod
    def handle_action(cls, user, pk: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an action on either a BreakPlan (by pk) or a BreakSuggestion (by pk).
        Returns dict with keys: break_plan, created (bool), action (str).
        Raises:
          - BreakPlan.DoesNotExist / BreakSuggestion.DoesNotExist when not found
          - serializers.ValidationError for invalid input
          - ValueError for other validation problems (e.g. duplicate)
        """
        # Try BreakPlan first
        try:
            bp = BreakPlan.objects.get(pk=pk, user=user)
            return cls._handle_plan_action(user, bp, data)
        except BreakPlan.DoesNotExist:
            # fall through to suggestion handling
            pass

        # Suggestion path
        try:
            suggestion = BreakSuggestion.objects.get(pk=pk, user=user)
        except BreakSuggestion.DoesNotExist:
            raise BreakPlan.DoesNotExist("Break plan/suggestion not found")

        if suggestion.is_accepted:
            raise ValueError("This suggested break has already been accepted.")

        # Validate action for suggestion
        serializer = BreakPlanActionSerializer(data=data, context={"break_plan": None})
        if not serializer.is_valid():
            raise serializers.ValidationError(serializer.errors)

        action = serializer.validated_data["action"]

        if action != "accept":
            raise ValueError("Only 'accept' action is supported for suggestions")

        # Create BreakPlan from suggestion inside a transaction
        with transaction.atomic():
            start_dt = datetime.combine(suggestion.start_date, time.min)
            end_dt = datetime.combine(suggestion.end_date, time.max)

            exists = BreakPlan.objects.filter(user=user, startDate=start_dt, endDate=end_dt).exists()
            if exists:
                raise ValueError("Break plan already exists for these dates")

            leave_balance = LeaveBalance.objects.filter(user=user).first()
            break_plan = BreakPlan.objects.create(
                user=user,
                leave_balance=leave_balance,
                startDate=start_dt,
                endDate=end_dt,
                description=suggestion.description or "",
                status="pending",
            )

            suggestion.is_accepted = True
            suggestion.save(update_fields=["is_accepted"])

            # create recommended BreakExecution
            try:
                BreakExecutionService.upsert_execution(
                    user=user,
                    recommended_start=suggestion.start_date,
                    recommended_end=suggestion.end_date,
                    status="recommended",
                )
            except Exception:
                logger.exception("Failed to upsert BreakExecution for accepted suggestion")

            return {"break_plan": break_plan, "created": True, "action": "accept"}

    @classmethod
    def _handle_plan_action(cls, user, break_plan: BreakPlan, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and apply an action to an existing BreakPlan.
        Returns dict with keys: break_plan, created(False), action
        """
        serializer = BreakPlanActionSerializer(data=data, context={"break_plan": break_plan})
        if not serializer.is_valid():
            raise serializers.ValidationError(serializer.errors)

        action = serializer.validated_data["action"]
        reason = serializer.validated_data.get("reason", "")

        action_to_status = {
            "approve": "approved",
            "reject": "rejected",
            "take": "taken",
            "miss": "missed",
            "cancel": "cancelled",
        }

        if action not in action_to_status:
            raise ValueError("Action not supported")

        new_status = action_to_status[action]

        # update model
        if reason:
            break_plan.description = f"{break_plan.description}\n\nAction: {action}\nReason: {reason}"
        break_plan.status = new_status
        break_plan.save()

        # Sync BreakExecution
        try:
            rec_start = break_plan.startDate.date()
            rec_end = break_plan.endDate.date()
            exec_status_map = {
                "approve": "approved",
                "reject": "rejected",
                "take": "taken",
                "miss": "missed",
                "cancel": "rejected",
            }
            exec_status = exec_status_map.get(action)
            actual_start = rec_start if action == "take" else None
            actual_end = rec_end if action == "take" else None

            BreakExecutionService.upsert_execution(
                user=user,
                recommended_start=rec_start,
                recommended_end=rec_end,
                status=exec_status,
                actual_start=actual_start,
                actual_end=actual_end,
            )
        except Exception:
            logger.exception("Failed to sync BreakExecution after plan action")

        return {"break_plan": break_plan, "created": False, "action": action}