# services/user_metrics_service.py

from datetime import timedelta
from django.utils import timezone
# from django.db.models import Count

from ..models.recommendation_models import UserMetrics
from ..models.preference_models import BreakPreferences
from ..models.date_models import DateEntry, SpecialDate, BlackoutDate
from ..models.working_pattern_models import WorkingPattern
from ..models.optimization_goal_models import OptimizationGoal
from ..models.mood_models import Mood
from ..models.break_execution import BreakExecution



class UserMetricsService:
    """
    Builds system-derived metrics used by the recommendation engine.
    """

    @staticmethod
    def build(user) -> UserMetrics:
        # print("🔁 Rebuilding metrics for:", user.id)
        metrics, _ = UserMetrics.objects.get_or_create(user=user)

        # --------------------------------------------------
        # 1. Work hours per week (WorkingPattern)
        # --------------------------------------------------
        metrics.work_hours_per_week = UserMetricsService._calculate_work_hours(user)

        # --------------------------------------------------
        # 2. Break preferences
        # --------------------------------------------------
        pref = BreakPreferences.objects.filter(user=user).first()
        if pref:
            metrics.break_type_preference = pref.preference
            metrics.prefers_travel = pref.weather_based_recommendation

        # --------------------------------------------------
        # 3. Optimization goals → season preference
        # --------------------------------------------------
        goal = OptimizationGoal.objects.filter(user=user).first()
        if goal and goal.preference == "avoid_peak_seasons":
            metrics.season_preference = "no_preference"

        # --------------------------------------------------
        # 4. Stress level (Mood-driven)
        # --------------------------------------------------
        metrics.stress_level = UserMetricsService._calculate_stress(user)

        # --------------------------------------------------
        # 5. Sleep quality (derived from mood & stability)
        # --------------------------------------------------
        metrics.sleep_quality = UserMetricsService._calculate_sleep_quality(user)

        metrics.save()
        return metrics

    # ============================
    # Helpers
    # ============================

    @staticmethod
    def _calculate_work_hours(user) -> int:
        pattern = getattr(user, "working_pattern", None)
        base_hours = 40

        if pattern:
            if pattern.pattern_type == "custom" and pattern.custom_days:
                base_hours = len(pattern.custom_days) * 8

            elif pattern.pattern_type == "shift" and pattern.days_on:
                base_hours = min(60, pattern.days_on * 8)

        # ---- Reduce hours by taken breaks (last 14 days) ----
        taken_breaks = BreakExecution.objects.filter(
            user=user,
            status="taken",
            actual_start__gte=timezone.now() - timedelta(days=14)
        )

        break_hours = 0
        for b in taken_breaks:
            if b.actual_start and b.actual_end:
                break_hours += (b.actual_end - b.actual_start).total_seconds() / 3600

        adjusted_hours = max(20, int(base_hours - break_hours))
        return adjusted_hours


    @staticmethod
    def _calculate_stress(user) -> int:
        recent_moods = Mood.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=14)
        )

        mood_weights = {
            "happy": 2,
            "excited": 3,
            "neutral": 5,
            "sad": 7,
            "anxious": 8,
            "angry": 9,
        }

        # ---- Base stress from mood ----
        if recent_moods.exists():
            mood_score = sum(mood_weights[m.mood_type] for m in recent_moods)
            mood_stress = mood_score // recent_moods.count()
        else:
            mood_stress = 5

        # ---- Break influence ----
        breaks = BreakExecution.objects.filter(
            user=user,
            recommended_start__gte=timezone.now() - timedelta(days=14)
        )

        taken = breaks.filter(status="taken").count()
        missed = breaks.filter(status="missed").count()

        # Each taken break reduces stress, missed increases it
        stress_adjustment = (missed * 1.5) - (taken * 2)

        final_stress = mood_stress + stress_adjustment

        return max(1, min(10, int(final_stress)))



    @staticmethod
    def _calculate_sleep_quality(user) -> int:
        last_7_days = timezone.now() - timedelta(days=7)

        moods = Mood.objects.filter(
            user=user,
            created_at__gte=last_7_days
        )

        breaks = BreakExecution.objects.filter(
            user=user,
            status="taken",
            actual_start__gte=last_7_days
        )

        # ---- Base quality from mood ----
        if moods.exists():
            negative = moods.filter(
                mood_type__in=["sad", "anxious", "angry"]
            ).count()
            base_quality = 10 - negative
        else:
            base_quality = 5

        # ---- Boost from breaks taken ----
        break_bonus = min(3, breaks.count())

        final_quality = base_quality + break_bonus

        return max(1, min(10, final_quality))

