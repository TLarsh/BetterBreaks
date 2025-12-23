from datetime import timedelta
from django.utils import timezone
from ..models.break_models import BreakScore, StreakScore, OptimizationScore
from ..models.badge_models import Badge
from django.db.models import Avg


class BadgeAwarder:

    @staticmethod
    def award_all(user):
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)

        # ---- Break counts ----
        all_breaks = BreakScore.objects.filter(user=user)
        recent_breaks = all_breaks.filter(score_date__gte=thirty_days_ago)

        weekend_breaks = all_breaks.filter(break_type='weekend').count()
        recent_weekend_breaks = recent_breaks.filter(break_type='weekend').count()
        holiday_breaks = all_breaks.filter(break_type='holiday').count()

        # ---- Streaks ----
        monthly_streak = StreakScore.objects.filter(
            user=user,
            streak_period='monthly'
        ).first()

        # ---- Optimization ----
        best_opt_score = OptimizationScore.objects.filter(
            user=user
        ).order_by('-score_value').first()

        # ---- Wellness ----
        wellbeing_avg = recent_breaks.aggregate(
            avg=Avg('wellbeing_impact')
        )['avg'] or 0

        # =====================================================
        # BADGE AWARDS
        # =====================================================

        if weekend_breaks >= 3:
            BadgeAwarder._award(
                user,
                'weekend_breaker',
                f'Took {weekend_breaks} weekend breaks',
                {'weekend_breaks': weekend_breaks}
            )

        if recent_weekend_breaks >= 2:
            BadgeAwarder._award(
                user,
                'weekend_recharger',
                'Recharged with multiple weekend breaks',
                {'recent_weekend_breaks': recent_weekend_breaks}
            )

        if holiday_breaks >= 2:
            BadgeAwarder._award(
                user,
                'holiday_master',
                f'Took {holiday_breaks} holiday breaks',
                {'holiday_breaks': holiday_breaks}
            )

        if monthly_streak and monthly_streak.current_streak >= 3:
            BadgeAwarder._award(
                user,
                'consistent_breaker',
                'Maintained a strong monthly break streak',
                {'monthly_streak': monthly_streak.current_streak}
            )

        if recent_breaks.count() >= 4:
            BadgeAwarder._award(
                user,
                'break_pro',
                'Took multiple breaks in a short period',
                {'recent_breaks': recent_breaks.count()}
            )

        if best_opt_score and best_opt_score.score_value >= 85:
            BadgeAwarder._award(
                user,
                'break_optimizer',
                'Achieved a high optimization score',
                {'optimization_score': best_opt_score.score_value}
            )

        if wellbeing_avg >= 4:
            BadgeAwarder._award(
                user,
                'wellness_warrior',
                'Maintained excellent wellbeing impact',
                {'avg_wellbeing': wellbeing_avg}
            )

        # Always awarded on successful taken break
        BadgeAwarder._award(
            user,
            'perfect_planner',
            'Planned and successfully took a break',
            {'taken_break': True}
        )

    @staticmethod
    def _award(user, badge_type, description, requirements):
        Badge.objects.get_or_create(
            user=user,
            badge_type=badge_type,
            defaults={
                'description': description,
                'requirements_met': requirements
            }
        )
