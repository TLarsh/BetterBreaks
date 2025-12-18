from django.db import transaction

from .break_score_service import BreakScoreService
from .streak_service import StreakService
from .optimization_service import OptimizationService


class BreakLifecycleService:

    @staticmethod
    @transaction.atomic
    def process_break_completion(break_exec):
        if break_exec.status != "taken":
            return

        break_date = break_exec.actual_start

        # 1️ Daily break score
        BreakScoreService.score_break(break_exec)

        # 2️ Update streak
        StreakService.update_streak(
            break_exec.user,
            break_date
        )

        # 3️ Optimization snapshot
        OptimizationService.calculate_daily_optimization(
            break_exec.user,
            break_date
        )
