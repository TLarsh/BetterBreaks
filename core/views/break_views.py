from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers 
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.timezone import now
from django.http import Http404
from datetime import datetime, timedelta, time
import random
import traceback
import logging
from ..serializers.break_serializers import (
    BreakPlanSerializer,
    BreakPlanUpdateSerializer,
    BreakPlanListSerializer,
    UpcomingBreakPlanSerializer,
)
from ..serializers.badge_serializers import BadgeSerializer
from ..serializers.score_serializers import BreakScoreSerializer, StreakScoreSerializer
from ..docs.break_docs import (
    # break_plan_list,
    # break_plan_create,
    # break_plan_update,
    # break_plan_delete,
    break_plan_action,
    break_log_list,
    break_log_create,
    break_log_update,
    break_log_delete,
    # break_log_summary,
    break_log_retrieve,
    recommend_breaks_schema,
)
from ..models.break_models import BreakPlan, BreakSuggestion, LeaveBalance
from ..serializers.break_serializers import BreakSuggestionSerializer, BreakPlanActionSerializer
from ..models.score_models import BreakScore, StreakScore 
from ..models.badge_models import Badge
from ..models.mood_models import Mood
from ..models.preference_models import BreakPreferences
from ..models.working_pattern_models import WorkingPattern
from ..models.date_models import BlackoutDate, SpecialDate
from ..utils.responses import success_response, error_response

logger = logging.getLogger(__name__)



from ..serializers.break_serializers import BreakRecommendationSerializer
from ..ml_engine.breaks_engine import generate_break_recommendation
from core.services.break_action_service import BreakPlanService


# --------------CREATE BREAK PLAN------------------

class CreateBreakPlanView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=BreakPlanSerializer)
    def post(self, request):
        serializer = BreakPlanSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            break_plan = serializer.save()
            return Response({
                "message": "Break plan created successfully.",
                "status": True,
                "data": BreakPlanSerializer(break_plan).data,
                "errors": None
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Invalid input.",
            "status": False,
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UpcomingBreaksView(APIView):
    """
    Get upcoming breaks for the logged-in user,
    respecting user's home_location_timezone.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = now().date()

        breaks = (
            BreakPlan.objects.filter(
                user=user,
                startDate__date__gte=today,
                status="approved"   # only approved breaks
            ).order_by("startDate")
        )

        if not breaks.exists():
            return success_response(
                message="No upcoming approved breaks found",
                data=[]
            )

        serializer = BreakPlanSerializer(breaks, many=True)
        return success_response(
            message="Fetched upcoming approved breaks successfully",
            data=serializer.data
        )


class ListUserBreakPlansView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'status', openapi.IN_QUERY,
                description="Status of the break plan (planned|pending|approved|rejected)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'year', openapi.IN_QUERY,
                description="Year to filter break plans by start date",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'limit', openapi.IN_QUERY,
                description="Number of items per page",
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'offset', openapi.IN_QUERY,
                description="Offset for pagination (default 0)",
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request):
        user = request.user
        status_param = request.query_params.get("status")
        year_param = request.query_params.get("year")
        limit = request.query_params.get("limit")
        offset = request.query_params.get("offset")

        try:
            # Initial Query
            plans_qs = BreakPlan.objects.filter(user=user)

            # Optional filters
            if status_param:
                plans_qs = plans_qs.filter(status=status_param)

            if year_param:
                try:
                    year = int(year_param)
                    plans_qs = plans_qs.filter(startDate__year=year)
                except ValueError:
                    return Response({
                        "message": "Invalid year format.",
                        "status": False,
                        "data": None,
                        "errors": {"year": ["Must be a valid integer"]}
                    }, status=status.HTTP_400_BAD_REQUEST)

            plans_qs = plans_qs.order_by("-created_at")

            limit = int(limit) if limit else 10
            offset = int(offset) if offset else 0

            paginator = Paginator(plans_qs, limit)
            page_number = (offset // limit) + 1

            if page_number > paginator.num_pages:
                return Response({
                    "message": "No more results.",
                    "status": True,
                    "data": {
                        "plans": [],
                        "total": paginator.count,
                        "hasMore": False
                    },
                    "errors": None
                }, status=status.HTTP_200_OK)

            current_page = paginator.page(page_number)
            serialized = BreakPlanListSerializer(current_page.object_list, many=True)

            return Response({
                "message": "Break plans retrieved successfully.",
                "status": True,
                "data": {
                    "plans": serialized.data,
                    "total": paginator.count,
                    "hasMore": current_page.has_next()
                },
                "errors": None
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": False,
                "data": None,
                "errors": {"server": [str(e)]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --------------UPDATE BREAK PLAN------------------
# Very high possibility i deprecate this view in future

class UpdateBreakPlanView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=BreakPlanUpdateSerializer,
        operation_description="Update a break plan. When a break plan is approved, gamification rewards are automatically created.",
        responses={
            200: openapi.Response(
                description="Break plan updated successfully with gamification rewards if approved",
                examples={
                    "application/json": {
                        "message": "Break plan updated successfully.",
                        "status": True,
                        "data": {
                            "plan": {
                                "id": "uuid-string",
                                "startDate": "2023-06-01T00:00:00Z",
                                "endDate": "2023-06-07T00:00:00Z",
                                "description": "Summer vacation",
                                "status": "approved",
                                "updatedAt": "2023-05-15T14:30:00Z"
                            },
                            "gamification": {
                                "break_score": {
                                    "id": 1,
                                    "score_date": "2023-06-01",
                                    "score_value": 10,
                                    "frequency_points": 5,
                                    "adherence_points": 5,
                                    "wellbeing_impact": "positive",
                                    "break_type": "vacation",
                                    "notes": "Break plan approved"
                                },
                                "streak": {
                                    "id": 1,
                                    "current_streak": 1,
                                    "longest_streak": 1,
                                    "streak_period": "monthly"
                                },
                                "recent_badges": [
                                    {
                                        "id": 1,
                                        "badge_type": "consistent_breaker",
                                        "level": 1,
                                        "description": "Took your first break!"
                                    }
                                ]
                            }
                        },
                        "errors": None
                    }
                }
            ),
            400: openapi.Response(description="Invalid input"),
            404: openapi.Response(description="Break plan not found"),
            500: openapi.Response(description="Server error")
        }
    )
    def put(self, request, planId):
        try:
            user = request.user

            if user.is_superuser or getattr(user, 'role', None) == 'admin':
                plan = get_object_or_404(BreakPlan, id=planId)
            else:
                plan = get_object_or_404(BreakPlan, id=planId, user=user)

            serializer = BreakPlanUpdateSerializer(plan, data=request.data)
            if serializer.is_valid():
                updated_plan = serializer.save()
                
                # Check if plan was approved and include gamification info
                gamification_data = None
                if updated_plan.status == 'approved':
                    # Get gamification data for the user
                    break_scores = BreakScore.objects.filter(user=user).order_by('-created_at')[:1]
                    streak_scores = StreakScore.objects.filter(user=user).order_by('-updated_at')[:1]
                    badges = Badge.objects.filter(user=user).order_by('-created_at')[:3]
                    
                    gamification_data = {
                        "break_score": BreakScoreSerializer(break_scores[0]).data if break_scores else None,
                        "streak": StreakScoreSerializer(streak_scores[0]).data if streak_scores else None,
                        "recent_badges": BadgeSerializer(badges, many=True).data if badges else [],
                    }
                
                return Response({
                    "message": "Break plan updated successfully.",
                    "status": True,
                    "data": {
                        "plan": {
                            "id": str(updated_plan.id),
                            "startDate": updated_plan.startDate,
                            "endDate": updated_plan.endDate,
                            "description": updated_plan.description,
                            "status": updated_plan.status,
                            "updatedAt": updated_plan.updated_at,
                        },
                        "gamification": gamification_data
                    },
                    "errors": None
                }, status=status.HTTP_200_OK)

            return Response({
                "message": "Validation failed.",
                "status": False,
                "data": None,
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            traceback.print_exc()
            logger.error(f"BreakPlan update error: {str(e)}")

            return Response({
                "message": "An unexpected error occurred.",
                "status": False,
                "data": None,
                "errors": {
                    "server": [str(e)]
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class DeleteBreakPlanView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Delete a break plan by its ID. Only the owner or an admin can perform this action.",
        manual_parameters=[
            openapi.Parameter(
                'planId',
                openapi.IN_PATH,
                description="ID of the break plan to delete",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Break plan deleted successfully.",
                examples={
                    "application/json": {
                        "message": "Break plan deleted successfully.",
                        "status": True,
                        "data": None,
                        "errors": None
                    }
                }
            ),
            403: openapi.Response(
                description="Forbidden - Not authorized to delete this plan."
            ),
            404: openapi.Response(
                description="Break plan not found."
            ),
            500: openapi.Response(
                description="Unexpected server error."
            ),
        }
    )
    def delete(self, request, planId):
        user = request.user

        try:
            plan = BreakPlan.objects.get(id=planId)
        except BreakPlan.DoesNotExist:
            return Response({
                "message": "Break plan not found.",
                "status": False,
                "data": None,
                "errors": {"planId": ["Invalid plan ID"]}
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                "message": "An unexpected error occurred.",
                "status": False,
                "data": None,
                "errors": {"server": [str(e)]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not (user.is_superuser or user.is_staff or getattr(user, 'role', '') == 'admin' or plan.user == user):
            return Response({
                "message": "You do not have permission to delete this plan.",
                "status": False,
                "data": None,
                "errors": {"permission": "Not authorized"}
            }, status=status.HTTP_403_FORBIDDEN)

        try:
            plan.delete()
            return Response({
                "message": "Break plan deleted successfully.",
                "status": True,
                "data": None,
                "errors": None
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "message": "An error occurred while deleting the break plan.",
                "status": False,
                "data": None,
                "errors": {"server": [str(e)]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class BreakSuggestionListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get all break suggestions for the current user"""
        suggestions = BreakSuggestion.objects.filter(user=request.user)
        serializer = BreakSuggestionSerializer(suggestions, many=True)
        return success_response(
            message="Break suggestions retrieved successfully",
            data=serializer.data
        )
    
    def post(self, request):
        """Generate a break suggestion based on user data"""
        try:
            user = request.user
            
            # Get user's mood, preferences, schedule, leave balance, blackout dates, special dates
            # This would typically come from various models
            leave_balance = LeaveBalance.objects.filter(user=user).first()
            if not leave_balance:
                return error_response(
                    message="Cannot generate suggestion",
                    errors={"leave_balance": "User has no leave balance set up"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
                
            # Check if user has enough leave balance
            if leave_balance.anual_leave_balance <= 0:
                return error_response(
                    message="Cannot generate suggestion",
                    errors={"leave_balance": "User has no leave days remaining"},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user's break preferences
            preferences = BreakPreferences.objects.filter(user=user).first()
            
            # Get user's working pattern
            working_pattern = WorkingPattern.objects.filter(user=user).first()
            
            # Get blackout dates
            blackout_dates = BlackoutDate.objects.filter(user=user)
            
            # Get special dates
            special_dates = SpecialDate.objects.filter(user=user)
            
            # Get user's recent mood
            recent_mood = Mood.objects.filter(user=user).order_by('-created_at').first()
            
            # Generate a suggestion based on collected data
            # This is a simplified algorithm - in a real system, this would be more sophisticated
            today = timezone.now().date()
            
            # Start with a date range in the next 30 days
            start_date = today + timedelta(days=random.randint(7, 14))
            end_date = start_date + timedelta(days=random.randint(1, 3))
            
            # Avoid weekends if working pattern exists
            if working_pattern:
                # Adjust to avoid weekends or non-working days based on pattern
                while start_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                    start_date += timedelta(days=1)
                while end_date.weekday() >= 5:
                    end_date += timedelta(days=1)
            
            # Avoid blackout dates
            for blackout in blackout_dates:
                # Convert datetime to date if needed
                blackout_start = blackout.start_date.date() if isinstance(blackout.start_date, datetime) else blackout.start_date
                blackout_end = blackout.end_date.date() if isinstance(blackout.end_date, datetime) else blackout.end_date
                
                if (blackout_start <= start_date <= blackout_end) or \
                   (blackout_start <= end_date <= blackout_end):
                    # Move dates forward past the blackout period
                    start_date = blackout_end + timedelta(days=1)
                    end_date = start_date + timedelta(days=random.randint(1, 3))
            
            # Prioritize special dates if any are coming up
            for special in special_dates:
                # Convert datetime to date if needed
                special_date = special.date.date() if isinstance(special.date, datetime) else special.date
                
                # If special date is within next 30 days, suggest a break around it
                if today <= special_date <= today + timedelta(days=30):
                    start_date = special_date - timedelta(days=1)
                    end_date = special_date + timedelta(days=1)
                    break
            
            # Generate title and description based on data
            title = "Suggested Break"
            description = "We recommend taking a break to recharge."
            reason = "Based on your schedule and preferences"
            
            # Adjust based on mood if available
            based_on_mood = False
            if recent_mood:
                based_on_mood = True
                # Map mood_type to a numeric score since Mood model doesn't have mood_score
                mood_scores = {
                    "happy": 8,
                    "sad": 3,
                    "angry": 2,
                    "neutral": 5,
                    "excited": 9,
                    "anxious": 3
                }
                mood_score = mood_scores.get(recent_mood.mood_type, 5)  # Default to 5 if unknown
                
                if mood_score < 5:  # Now using our mapped score
                    title = "Wellness Break"
                    description = "Your recent mood indicates you could benefit from some time off."
                    reason = "Based on your recent mood tracking"
            
            # Create the suggestion
            suggestion = BreakSuggestion.objects.create(
                user=user,
                title=title,
                description=description,
                start_date=start_date,
                end_date=end_date,
                reason=reason,
                priority=10 if based_on_mood else 5,  # Using numeric values for priority
                based_on_mood=based_on_mood,
                based_on_workload=True,
                based_on_preferences=preferences is not None,
                based_on_weather=False  # Would require weather API integration
            )
            
            serializer = BreakSuggestionSerializer(suggestion)
            return success_response(
                message="Break suggestion generated successfully",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            return error_response(
                message="Failed to generate break suggestion",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# class BreakPlanActionView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self, pk, user):
#         try:
#             return BreakPlan.objects.get(pk=pk, user=user)
#         except BreakPlan.DoesNotExist:
#             return None

#     @break_plan_action
#     def patch(self, request, pk):
#         try:
#             user = request.user
#             break_plan = self.get_object(pk, user)
            
#             # If not found in BreakPlan, check BreakSuggestion
#             if not break_plan:
#                 try:
#                     suggestion = BreakSuggestion.objects.get(pk=pk, user=user)
#                 except BreakSuggestion.DoesNotExist:
#                     return error_response(
#                         message="Break plan/suggestion not found",
#                         errors={"break_plan": "Break plan/suggestion not found or you don't have permission"},
#                         status_code=status.HTTP_404_NOT_FOUND
#                     )
                
#                 # Prevent duplicate addition if already accepted
#                 if suggestion.is_accepted:
#                     return error_response(
#                         message="This suggested break has already been accepted.",
#                         errors={"break_suggestion": "Already accepted and added to break plan."},
#                         status_code=status.HTTP_409_CONFLICT
#                     )
                
#                 # Validate the action
#                 serializer = BreakPlanActionSerializer(data=request.data, context={'break_plan': None})
#                 if not serializer.is_valid():
#                     return error_response(
#                         message="Invalid action",
#                         errors=serializer.errors,
#                         status_code=status.HTTP_400_BAD_REQUEST
#                     )
                
#                 action = serializer.validated_data['action']
#                 reason = serializer.validated_data.get('reason', '')

#                 # Only create BreakPlan if action is 'accept'
#                 if action == 'accept':
#                     exists = BreakPlan.objects.filter(
#                         user=user,
#                         startDate=datetime.combine(suggestion.start_date, time.min),
#                         endDate=datetime.combine(suggestion.end_date, time.max)
#                     ).exists()
#                     if exists:
#                         return error_response(
#                             message="Break plan already exists for these dates",
#                             errors={"break_plan": "Duplicate break plan"},
#                             status_code=status.HTTP_409_CONFLICT
#                         )
#                     # Create BreakPlan from suggestion
#                     break_plan = BreakPlan.objects.create(
#                         user=user,
#                         leave_balance=LeaveBalance.objects.filter(user=user).first(),
#                         startDate=datetime.combine(suggestion.start_date, time.min),
#                         endDate=datetime.combine(suggestion.end_date, time.max),
#                         description=suggestion.description,
#                         status='pending',
#                     )
#                     # Mark suggestion as accepted
#                     suggestion.is_accepted = True
#                     suggestion.save(update_fields=["is_accepted"])
#                     return success_response(
#                         message="Break plan created from suggestion",
#                         data=BreakPlanSerializer(break_plan).data,
#                         status_code=status.HTTP_201_CREATED
#                     )
#                 else:
#                     return error_response(
#                         message="Only 'accept' action is supported for suggestions",
#                         errors={"action": "Invalid action for suggestion"},
#                         status_code=status.HTTP_400_BAD_REQUEST
#                     )
            
#             # If found in BreakPlan, proceed as before
#             serializer = BreakPlanActionSerializer(data=request.data, context={'break_plan': break_plan})
#             if not serializer.is_valid():
#                 return error_response(
#                     message="Invalid action",
#                     errors=serializer.errors,
#                     status_code=status.HTTP_400_BAD_REQUEST
#                 )
            
#             action = serializer.validated_data['action']
#             reason = serializer.validated_data.get('reason', '')
            
#             action_to_status = {
#                 'approve': 'approved',
#                 'reject': 'rejected',
#                 'take': 'taken',
#                 'miss': 'missed',
#                 'cancel': 'cancelled'
#             }
            
#             if action in action_to_status:
#                 break_plan.status = action_to_status[action]
#                 if reason:
#                     break_plan.description = f"{break_plan.description}\n\nAction: {action}\nReason: {reason}"
#                 break_plan.save()
#                 return success_response(
#                     message=f"Break successfully {action_to_status[action]}",
#                     data=BreakPlanSerializer(break_plan).data
#                 )
#             else:
#                 return error_response(
#                     message="Invalid action",
#                     errors={"action": "Action not supported"},
#                     status_code=status.HTTP_400_BAD_REQUEST
#                 )
            
#         except Exception as e:
#             return error_response(
#                 message="Failed to update break plan",
#                 errors={"detail": str(e)},
#                 status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
#             )



class BreakPlanActionView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk, user):
        try:
            return BreakPlan.objects.get(pk=pk, user=user)
        except BreakPlan.DoesNotExist:
            return None

    @break_plan_action
    def patch(self, request, pk):
        try:
            user = request.user
            result = BreakPlanService.handle_action(user, pk, request.data)
            bp = result["break_plan"]
            if result.get("created"):
                return success_response(
                    message="Break plan created from suggestion",
                    data=BreakPlanSerializer(bp).data,
                    status_code=status.HTTP_201_CREATED
                )
            else:
                return success_response(
                    message=f"Break successfully {bp.status}",
                    data=BreakPlanSerializer(bp).data
                )

        except BreakPlan.DoesNotExist:
            return error_response(
                message="Break plan/suggestion not found",
                errors={"break_plan": "Break plan/suggestion not found or you don't have permission"},
                status_code=status.HTTP_404_NOT_FOUND
            )
        except serializers.ValidationError as ve:
            return error_response(
                message="Invalid action",
                errors=ve.detail if hasattr(ve, "detail") else ve.args,
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except ValueError as ve:
            return error_response(
                message=str(ve),
                errors={"detail": str(ve)},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return error_response(
                message="Failed to update break plan",
                errors={"detail": str(e)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BreakLogListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @break_log_list
    def get(self, request):
        """Get all break logs for the current user"""
        break_scores = BreakScore.objects.filter(user=request.user)
        serializer = BreakScoreSerializer(break_scores, many=True)
        return Response(serializer.data)
    
    @break_log_create
    def post(self, request):
        """Log when a user takes a break"""
        serializer = BreakScoreSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
       
        break_score = serializer.save(user=request.user)
        
       
        streak, created = StreakScore.objects.get_or_create(
            user=request.user,
            streak_period=request.data.get('streak_period', 'monthly')
        )
        streak.increment_streak(break_score.score_date)
        streak.save()
        
       
        user = request.user
        user.total_break_score += break_score.score_value
        if streak.longest_streak > user.highest_streak:
            user.highest_streak = streak.longest_streak
        user.save()
        
        return Response(serializer.data, status=201)

class BreakLogDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return BreakScore.objects.get(pk=pk, user=self.request.user)
        except BreakScore.DoesNotExist:
            raise Http404
    
    @break_log_retrieve
    def get(self, request, pk):
        """Get a specific break log"""
        break_score = self.get_object(pk)
        serializer = BreakScoreSerializer(break_score)
        return Response(serializer.data)
    
    @break_log_update
    def put(self, request, pk):
        """Update a specific break log"""
        break_score = self.get_object(pk)
        serializer = BreakScoreSerializer(break_score, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @break_log_delete
    def delete(self, request, pk):
        """Delete a specific break log"""
        break_score = self.get_object(pk)
        break_score.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



