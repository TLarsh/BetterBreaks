import os
import sys
from datetime import date, timedelta

# Add the ml_engine directory to the path so we can import from it
from django.conf import settings
from ..models.recommendation_models import UserMetrics, BreakRecommendation
from ..models.break_models import BreakPlan
from ..models.user_models import User
from ..models.holiday_models import PublicHolidayCalendar

# Import the ML engine
sys.path.append(os.path.join(settings.BASE_DIR, 'core/ml_engine'))
from core.ml_engine.breaks_engine import generate_break_recommendation


class RecommendationService:
    """Service for generating break recommendations using the ML engine"""
    
    @staticmethod
    def get_user_input_dict(user_metrics):
        """Convert UserMetrics model to input dict for ML engine"""
        # Map Django model fields to ML engine input format
        return {
            "work_hours_per_week": user_metrics.work_hours_per_week,
            "stress_level": user_metrics.stress_level,
            "sleep_quality": user_metrics.sleep_quality,
            "prefers_travel": user_metrics.prefers_travel,
            "season_preference": user_metrics.season_preference
        }
    
    @staticmethod
    def generate_recommendation(user):
        """Generate a break recommendation for a user"""
        try:
            # Get user metrics
            user_metrics = UserMetrics.objects.get(user=user)
            
            # Check if user already has a recent recommendation (within last 7 days)
            recent_recommendation = BreakRecommendation.objects.filter(
                user=user,
                created_at__gte=date.today() - timedelta(days=7)
            ).first()
            
            # If recent recommendation exists, return it instead of creating a new one
            if recent_recommendation:
                return recent_recommendation
            
            # Convert to input dict for ML engine
            user_input = RecommendationService.get_user_input_dict(user_metrics)
            
            # Generate recommendation using ML engine
            recommendation_data = generate_break_recommendation(user_input)
            
            # Create BreakRecommendation object
            recommendation = BreakRecommendation.objects.create(
                user=user,
                recommended_start_date=date.fromisoformat(recommendation_data['recommended_start_date']),
                recommended_end_date=date.fromisoformat(recommendation_data['recommended_end_date']),
                predicted_length_days=recommendation_data['predicted_length_days'],
                recommended_season=recommendation_data['recommended_season'],
                message=recommendation_data['message']
            )
            
            return recommendation
        except UserMetrics.DoesNotExist:
            # If user doesn't have metrics, create default ones
            user_metrics = UserMetrics.objects.create(user=user)
            return RecommendationService.generate_recommendation(user)
        except Exception as e:
            # Log error with more details
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating recommendation: {str(e)}")
            logger.error(f"User metrics: {user_metrics.__dict__}")
            return None
    
    @staticmethod
    def optimize_around_holidays(user, start_date, end_date):
        """Optimize break dates around public holidays"""
        try:
            # Get user's holiday calendar
            calendar = PublicHolidayCalendar.objects.filter(country=user.home_location_timezone).first()
            if not calendar:
                return start_date, end_date
            
            # Get holidays in the date range +/- 14 days
            search_start = start_date - timedelta(days=14)
            search_end = end_date + timedelta(days=14)
            
            holidays = calendar.holidays.filter(
                date__gte=search_start,
                date__lte=search_end
            ).values_list('date', flat=True)
            
            # If no holidays found, return original dates
            if not holidays:
                return start_date, end_date
            
            # Find closest holiday to start_date
            closest_holiday = min(holidays, key=lambda x: abs((x - start_date).days))
            
            # If holiday is within 3 days of start_date, adjust start_date to include it
            if abs((closest_holiday - start_date).days) <= 3:
                if closest_holiday < start_date:
                    # Holiday is before start_date
                    new_start = closest_holiday
                    new_end = end_date + (start_date - closest_holiday)
                else:
                    # Holiday is after start_date
                    new_start = start_date
                    new_end = end_date + (closest_holiday - start_date)
                
                return new_start, new_end
            
            return start_date, end_date
        except Exception as e:
            # Log error
            print(f"Error optimizing around holidays: {str(e)}")
            return start_date, end_date
    
    @staticmethod
    def convert_recommendation_to_break_plan(recommendation, user):
        """Convert a recommendation to a break plan"""
        from ..models.leave_balance_models import LeaveBalance
        
        # Get or create leave balance
        leave_balance, _ = LeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                "anual_leave_balance": 60,
                "anual_leave_refresh_date": date.today().replace(year=date.today().year + 1),
                "already_used_balance": 0,
            }
        )
        
        # Create break plan
        break_plan = BreakPlan.objects.create(
            user=user,
            leave_balance=leave_balance,
            startDate=recommendation.recommended_start_date,
            endDate=recommendation.recommended_end_date,
            description=f"Recommended break: {recommendation.message}",
            type='vacation',
            status='planned'
        )
        
        return break_plan