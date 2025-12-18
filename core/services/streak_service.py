# services/streak_service.py

from ..models.score_models import StreakScore


class StreakService:

    @staticmethod
    def update_streak(user, break_date):
        streak, _ = StreakScore.objects.get_or_create(
            user=user,
            streak_period="monthly"
        )

        streak.increment_streak(break_date)
        streak.save()

        return streak
