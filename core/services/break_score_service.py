# services/break_score_service.py

from django.utils import timezone
from datetime import timedelta


from ..models.score_models import BreakScore
from ..models.break_execution import BreakExecution


class BreakScoreService:

    @staticmethod
    def score_break(break_exec: BreakExecution):
        date = break_exec.actual_start or break_exec.recommended_start

        score, _ = BreakScore.objects.get_or_create(
            user=break_exec.user,
            score_date=date
        )

        # -------- Frequency points --------
        score.frequency_points = 5

        # -------- Adherence points --------
        if break_exec.status == "taken":
            score.adherence_points = 10
        else:
            score.adherence_points = 0

        # -------- Wellbeing impact --------
        duration = break_exec.duration()
        score.wellbeing_impact = max(-5, min(10, duration * 2))

        score.break_type = "personal"
        score.calculate_total_score()
        score.save()

        return score
