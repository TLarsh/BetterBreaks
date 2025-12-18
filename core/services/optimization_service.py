# services/optimization_service.py

from django.utils import timezone

from ..models.score_models import OptimizationScore, BreakScore, StreakScore


class OptimizationService:

    @staticmethod
    def calculate_daily_optimization(user, date):
        break_score = BreakScore.objects.filter(
            user=user, score_date=date
        ).first()

        streak = StreakScore.objects.filter(
            user=user, streak_period="monthly"
        ).first()

        optimization, _ = OptimizationScore.objects.get_or_create(
            user=user,
            score_date=date
        )

        # -------- Component scores --------
        optimization.break_timing_score = (
            break_score.adherence_points if break_score else 0
        )

        optimization.break_frequency_score = (
            break_score.frequency_points if break_score else 0
        )

        optimization.break_consistency_score = (
            min(streak.current_streak * 5, 100) if streak else 0
        )

        optimization.calculate_total_score()

        optimization.recommendations = [
            "Maintain consistent monthly breaks",
            "Avoid skipping recommended breaks"
        ]

        optimization.save()
        return optimization
