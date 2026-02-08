from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import transaction, IntegrityError
import traceback
from ..serializers.optimization_goal_serializers import OptimizationGoalSerializer
from ..serializers.date_serializers import BlackOutDateSerializer
from ..serializers.working_pattern_serializers import WorkingPatternSerializer
from ..models.optimization_goal_models import OptimizationGoal
from ..models.working_pattern_models import WorkingPattern
from ..models.date_models import BlackoutDate
from ..utils.responses import success_response, error_response
from ..docs.schedule_docs import (
    schedule_get_schema,
    schedule_post_schema
)



###### SCHEDULE #####################################
class ScheduleView(APIView):
    """
    Combined view to GET or POST WorkingPattern, BlackoutDates, and OptimizationGoals
    📌 For "rotation_pattern" input one of the following enum; "1_week, 2_weeks, 3_weeks",
    📌 For "shift_preview" input an array ; "ON, ON, ON, OFF, OFF, ON, ON",
    📌 For "shift_preview" input an array, example; "Mon, Wed, Friday",

    """

    @schedule_get_schema
    def get(self, request):
        user = request.user
        try:
            working_pattern = WorkingPattern.objects.filter(user=user).first()
            blackout_dates = BlackoutDate.objects.filter(user=user)
            optimization_goals = OptimizationGoal.objects.filter(user=user)

            data = {
                "working_pattern": WorkingPatternSerializer(working_pattern).data if working_pattern else None,
                "blackout_dates": BlackOutDateSerializer(blackout_dates, many=True).data,
                "optimization_goals": OptimizationGoalSerializer(optimization_goals, many=True).data,
            }

            return Response({
                "message": "Schedule retrieved successfully.",
                "status": True,
                "data": data,
                "errors": None
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "Internal server error.",
                "status": False,
                "data": None,
                "errors": {
                    "non_field_errors": [str(e)],
                    "traceback": traceback.format_exc().splitlines()
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @schedule_post_schema
    def post(self, request):
        user = request.user
        data = request.data

        try:
            with transaction.atomic():
                # === WORKING PATTERN ===
                wp_data = data.get('working_pattern')
                if wp_data:
                    wp_instance, _ = WorkingPattern.objects.get_or_create(user=user)
                    wp_serializer = WorkingPatternSerializer(wp_instance, data=wp_data, partial=True)
                    wp_serializer.is_valid(raise_exception=True)
                    wp_serializer.save()

                # === BLACKOUT DATES ===
                blackout_data = data.get('blackout_dates', [])
                BlackoutDate.objects.filter(user=user).delete()
                if blackout_data:
                    blackout_serializer = BlackOutDateSerializer(
                        data=blackout_data,
                        many=True,
                        context={"request": request}
                    )
                    blackout_serializer.is_valid(raise_exception=True)
                    blackout_serializer.save()

                # === OPTIMIZATION GOALS ===
                OptimizationGoal.objects.filter(user=user).delete()
                goal_data = data.get('optimization_goals', [])
                goal_objects = [OptimizationGoal(user=user, preference=pref) for pref in goal_data]
                OptimizationGoal.objects.bulk_create(goal_objects)

                return Response({
                    "message": "Schedule updated successfully.",
                    "status": True,
                    "data": None,
                    "errors": None
                }, status=status.HTTP_200_OK)

        except DRFValidationError as ve:
            return Response({
                "message": "Validation failed.",
                "status": False,
                "data": None,
                "errors": ve.detail
            }, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as ie:
            return Response({
                "message": "Database integrity error.",
                "status": False,
                "data": None,
                "errors": {"non_field_errors": [str(ie)]}
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": False,
                "data": None,
                "errors": {
                    "non_field_errors": [str(e)],
                    "traceback": traceback.format_exc().splitlines()
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
