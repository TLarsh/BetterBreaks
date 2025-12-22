import logging
from datetime import date, timedelta

from django.utils import timezone

from ..models.recommendation_models import UserMetrics, BreakRecommendation
from ..models.break_models import BreakPlan
from ..models.user_models import User
from ..models.holiday_models import PublicHolidayCalendar
from ..models.leave_balance_models import LeaveBalance

from core.ml_engine.breaks_engine import generate_break_recommendation

logger = logging.getLogger(__name__)


class RecommendationService:
    """
    Service for generating break recommendations using the ML engine.
    Relies ONLY on system-derived UserMetrics.
    """

    # ------------------------------------------------------------------
    # Metrics → ML input
    # ------------------------------------------------------------------
    @staticmethod
    def get_user_input_dict(user_metrics: UserMetrics) -> dict:
        """Convert UserMetrics model to input dict for ML engine"""
        return {
            "work_hours_per_week": user_metrics.work_hours_per_week,
            "stress_level": user_metrics.stress_level,
            "sleep_quality": user_metrics.sleep_quality,
            "prefers_travel": user_metrics.prefers_travel,
            "season_preference": user_metrics.season_preference,
        }

    # ------------------------------------------------------------------
    # Recommendation generation
    # ------------------------------------------------------------------
    @staticmethod
    def generate_recommendation(user: User) -> BreakRecommendation | None:
        """
        Generate a break recommendation for a user.
        Returns existing recent recommendation if found.
        """
        try:
            # Metrics must exist (built by UserMetricsService)
            user_metrics = UserMetrics.objects.get(user=user)

            # Avoid spamming recommendations (7-day window)
            recent_recommendation = BreakRecommendation.objects.filter(
                user=user,
                created_at__gte=timezone.now() - timedelta(days=7),
            ).first()

            if recent_recommendation:
                return recent_recommendation

            # ML input
            user_input = RecommendationService.get_user_input_dict(user_metrics)

            # Generate via ML / heuristic engine
            recommendation_data = generate_break_recommendation(user_input)

            # Parse dates safely
            start_date = date.fromisoformat(
                recommendation_data["recommended_start_date"]
            )
            end_date = date.fromisoformat(
                recommendation_data["recommended_end_date"]
            )

            # Optimize around public holidays
            optimized_start, optimized_end = (
                RecommendationService.optimize_around_holidays(
                    user, start_date, end_date
                )
            )

            # Persist recommendation
            recommendation = BreakRecommendation.objects.create(
                user=user,
                recommended_start_date=optimized_start,
                recommended_end_date=optimized_end,
                predicted_length_days=recommendation_data.get(
                    "predicted_length_days",
                    (optimized_end - optimized_start).days,
                ),
                recommended_season=recommendation_data.get("recommended_season"),
                message=recommendation_data.get("message", ""),
            )

            return recommendation

        except UserMetrics.DoesNotExist:
            logger.warning(
                f"Cannot generate recommendation — metrics missing for user {user.id}"
            )
            return None

        except Exception as e:
            logger.error(
                f"Error generating recommendation for user {user.id}: {str(e)}",
                exc_info=True,
            )
            return None

    # ------------------------------------------------------------------
    # Holiday optimization
    # ------------------------------------------------------------------
    @staticmethod
    def optimize_around_holidays(
        user: User, start_date: date, end_date: date
    ) -> tuple[date, date]:
        """
        Adjust break dates to include nearby public holidays (+/- 14 days).
        """
        try:
            calendar = PublicHolidayCalendar.objects.filter(user=user).first()
            if not calendar or not calendar.is_enabled:
                return start_date, end_date

            search_start = start_date - timedelta(days=14)
            search_end = end_date + timedelta(days=14)

            holidays = list(
                calendar.holidays.filter(
                    date__gte=search_start,
                    date__lte=search_end,
                ).values_list("date", flat=True)
            )

            if not holidays:
                return start_date, end_date

            closest_holiday = min(
                holidays, key=lambda d: abs((d - start_date).days)
            )

            if abs((closest_holiday - start_date).days) <= 3:
                if closest_holiday < start_date:
                    delta = start_date - closest_holiday
                    return closest_holiday, end_date + delta
                else:
                    delta = closest_holiday - start_date
                    return start_date, end_date + delta

            return start_date, end_date

        except Exception as e:
            logger.warning(
                f"Holiday optimization failed for user {user.id}: {str(e)}"
            )
            return start_date, end_date

    # ------------------------------------------------------------------
    # Recommendation → BreakPlan
    # ------------------------------------------------------------------
    @staticmethod
    def convert_recommendation_to_break_plan(
        recommendation: BreakRecommendation, user: User
    ) -> BreakPlan:
        """Convert a recommendation into a planned BreakPlan."""
        leave_balance, _ = LeaveBalance.objects.get_or_create(
            user=user,
            defaults={
                "anual_leave_balance": 60,
                "anual_leave_refresh_date": date.today().replace(
                    year=date.today().year + 1
                ),
                "already_used_balance": 0,
            },
        )

        break_plan = BreakPlan.objects.create(
            user=user,
            leave_balance=leave_balance,
            startDate=recommendation.recommended_start_date,
            endDate=recommendation.recommended_end_date,
            description=f"Recommended break: {recommendation.message}",
            type="vacation",
            status="planned",
        )

        return break_plan
