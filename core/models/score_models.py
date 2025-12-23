from django.db import models
from django.utils import timezone
from datetime import timedelta
from .user_models import User
from .badge_models import Badge


########## BREAK SCORE MODELS #############################

class BreakScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='break_scores')
    score_date = models.DateField()
    score_value = models.IntegerField(default=0)
    frequency_points = models.IntegerField(default=0)
    adherence_points = models.IntegerField(default=0)
    wellbeing_impact = models.IntegerField(default=0)
    break_type = models.CharField(
        max_length=50,
        choices=[
            ('holiday', 'Public Holiday'),
            ('weekend', 'Weekend'),
            ('personal', 'Personal Break'),
        ]
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'score_date')
        ordering = ['-score_date']

    def __str__(self):
        return f"{self.user.email} - {self.score_date} ({self.score_value})"

    def calculate_total_score(self):
        self.score_value = (
            self.frequency_points +
            self.adherence_points +
            self.wellbeing_impact
        )
        return self.score_value

    # def award_badges(self):
    #     """Award badges based on break activity."""
    #     thirty_days_ago = timezone.now().date() - timedelta(days=30)

    #     recent_breaks = BreakScore.objects.filter(
    #         user=self.user,
    #         score_date__gte=thirty_days_ago
    #     ).count()

    #     # Break Pro badge
    #     if recent_breaks >= 4:
    #         Badge.objects.get_or_create(
    #             user=self.user,
    #             badge_type='break_pro',
    #             defaults={
    #                 'description': f'Took {recent_breaks} breaks in the last 30 days',
    #                 'requirements_met': {'recent_breaks': recent_breaks}
    #             }
    #         )

    #     # Perfect Planner badge
    #     if self.score_value > 0:
    #         Badge.objects.get_or_create(
    #             user=self.user,
    #             badge_type='perfect_planner',
    #             defaults={
    #                 'description': 'Planned and took a break successfully',
    #                 'requirements_met': {'break_score': self.score_value}
    #             }
    #         )


########## STREAK SCORE MODELS #############################

class StreakScore(models.Model):
    STREAK_PERIOD_CHOICES = [
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streak_scores')
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    streak_period = models.CharField(
        max_length=20,
        choices=STREAK_PERIOD_CHOICES,
        default='monthly'
    )
    last_break_date = models.DateField(null=True, blank=True)
    streak_start_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'streak_period')

    def __str__(self):
        return f"{self.user.email} - {self.streak_period} streak ({self.current_streak})"

    def increment_streak(self, break_date):
        if not self.last_break_date:
            self.current_streak = 1
            self.longest_streak = 1
            self.streak_start_date = break_date
        elif self._is_consecutive(break_date):
            self.current_streak += 1
            self.longest_streak = max(self.longest_streak, self.current_streak)
        else:
            self.current_streak = 1
            self.streak_start_date = break_date

        self.last_break_date = break_date
        return self.current_streak

    def _is_consecutive(self, break_date):
        if not self.last_break_date:
            return False

        if self.streak_period == 'weekly':
            last_week = self.last_break_date.isocalendar()[1]
            current_week = break_date.isocalendar()[1]
            return (
                current_week - last_week == 1 or
                (last_week == 52 and current_week == 1)
            )

        if self.streak_period == 'monthly':
            return (
                (break_date.year == self.last_break_date.year and
                 break_date.month - self.last_break_date.month == 1) or
                (self.last_break_date.month == 12 and break_date.month == 1)
            )

        if self.streak_period == 'yearly':
            return break_date.year - self.last_break_date.year == 1

        return False

    # def award_badges(self):
    #     """Award badges based on streaks."""
    #     if self.current_streak >= 3:
    #         Badge.objects.get_or_create(
    #             user=self.user,
    #             badge_type='consistent_breaker',
    #             defaults={
    #                 'description': (
    #                     f'Maintained a {self.current_streak} '
    #                     f'{self.streak_period} break streak'
    #                 ),
    #                 'requirements_met': {
    #                     'streak_period': self.streak_period,
    #                     'current_streak': self.current_streak
    #                 }
    #             }
    #         )


########## OPTIMIZATION SCORE MODELS #############################

class OptimizationScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='optimization_scores')
    score_date = models.DateField()
    score_value = models.FloatField(default=0.0)
    break_timing_score = models.FloatField(default=0.0)
    break_frequency_score = models.FloatField(default=0.0)
    break_consistency_score = models.FloatField(default=0.0)
    notes = models.TextField(blank=True, null=True)
    recommendations = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'score_date')
        ordering = ['-score_date']

    def __str__(self):
        return f"{self.user.email} - Optimization ({self.score_value})"

    def calculate_total_score(self):
        timing_weight = 0.4
        frequency_weight = 0.3
        consistency_weight = 0.3

        self.score_value = (
            self.break_timing_score * timing_weight +
            self.break_frequency_score * frequency_weight +
            self.break_consistency_score * consistency_weight
        )
        return self.score_value

    # def award_badges(self):
    #     """Award badges for strong optimization habits."""
    #     if self.score_value >= 85:
    #         Badge.objects.get_or_create(
    #             user=self.user,
    #             badge_type='break_optimizer',
    #             defaults={
    #                 'description': 'Achieved a high break optimization score',
    #                 'requirements_met': {'optimization_score': self.score_value}
    #             }
    #         )









# from django.db import models
# from django.utils import timezone
# from datetime import timedelta
# from .user_models import User
# from .badge_models import Badge


# ########## BREAK SCORE MODELS #############################

# class BreakScore(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='break_scores')
#     score_date = models.DateField()
#     score_value = models.IntegerField(default=0)
#     frequency_points = models.IntegerField(default=0)
#     adherence_points = models.IntegerField(default=0)
#     wellbeing_impact = models.IntegerField(default=0)
#     break_type = models.CharField(
#         max_length=50,
#         choices=[
#             ('holiday', 'Public Holiday'),
#             ('weekend', 'Weekend'),
#             ('personal', 'Personal Break'),
#         ]
#     )
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('user', 'score_date')
#         ordering = ['-score_date']

#     def __str__(self):
#         return f"{self.user.email} - {self.score_date} ({self.score_value})"

#     def calculate_total_score(self):
#         self.score_value = (
#             self.frequency_points +
#             self.adherence_points +
#             self.wellbeing_impact
#         )
#         return self.score_value

#     def award_badges(self):
#         """Award badges based on break activity."""
#         thirty_days_ago = timezone.now().date() - timedelta(days=30)

#         recent_breaks = BreakScore.objects.filter(
#             user=self.user,
#             score_date__gte=thirty_days_ago
#         ).count()

#         # Break Pro badge
#         if recent_breaks >= 4:
#             Badge.objects.get_or_create(
#                 user=self.user,
#                 badge_type='break_pro',
#                 defaults={
#                     'description': f'Took {recent_breaks} breaks in the last 30 days',
#                     'requirements_met': {'recent_breaks': recent_breaks}
#                 }
#             )

#         # Perfect Planner badge
#         if self.score_value > 0:
#             Badge.objects.get_or_create(
#                 user=self.user,
#                 badge_type='perfect_planner',
#                 defaults={
#                     'description': 'Planned and took a break successfully',
#                     'requirements_met': {'break_score': self.score_value}
#                 }
#             )


# ########## STREAK SCORE MODELS #############################

# class StreakScore(models.Model):
#     STREAK_PERIOD_CHOICES = [
#         ('weekly', 'Weekly'),
#         ('monthly', 'Monthly'),
#         ('yearly', 'Yearly'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='streak_scores')
#     current_streak = models.PositiveIntegerField(default=0)
#     longest_streak = models.PositiveIntegerField(default=0)
#     streak_period = models.CharField(
#         max_length=20,
#         choices=STREAK_PERIOD_CHOICES,
#         default='monthly'
#     )
#     last_break_date = models.DateField(null=True, blank=True)
#     streak_start_date = models.DateField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('user', 'streak_period')

#     def __str__(self):
#         return f"{self.user.email} - {self.streak_period} streak ({self.current_streak})"

#     def increment_streak(self, break_date):
#         if not self.last_break_date:
#             self.current_streak = 1
#             self.longest_streak = 1
#             self.streak_start_date = break_date
#         elif self._is_consecutive(break_date):
#             self.current_streak += 1
#             self.longest_streak = max(self.longest_streak, self.current_streak)
#         else:
#             self.current_streak = 1
#             self.streak_start_date = break_date

#         self.last_break_date = break_date
#         return self.current_streak

#     def _is_consecutive(self, break_date):
#         if not self.last_break_date:
#             return False

#         if self.streak_period == 'weekly':
#             last_week = self.last_break_date.isocalendar()[1]
#             current_week = break_date.isocalendar()[1]
#             return (
#                 current_week - last_week == 1 or
#                 (last_week == 52 and current_week == 1)
#             )

#         if self.streak_period == 'monthly':
#             return (
#                 (break_date.year == self.last_break_date.year and
#                  break_date.month - self.last_break_date.month == 1) or
#                 (self.last_break_date.month == 12 and break_date.month == 1)
#             )

#         if self.streak_period == 'yearly':
#             return break_date.year - self.last_break_date.year == 1

#         return False

#     def award_badges(self):
#         """Award badges based on streaks."""
#         if self.current_streak >= 3:
#             Badge.objects.get_or_create(
#                 user=self.user,
#                 badge_type='consistent_breaker',
#                 defaults={
#                     'description': (
#                         f'Maintained a {self.current_streak} '
#                         f'{self.streak_period} break streak'
#                     ),
#                     'requirements_met': {
#                         'streak_period': self.streak_period,
#                         'current_streak': self.current_streak
#                     }
#                 }
#             )


# ########## OPTIMIZATION SCORE MODELS #############################

# class OptimizationScore(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='optimization_scores')
#     score_date = models.DateField()
#     score_value = models.FloatField(default=0.0)
#     break_timing_score = models.FloatField(default=0.0)
#     break_frequency_score = models.FloatField(default=0.0)
#     break_consistency_score = models.FloatField(default=0.0)
#     notes = models.TextField(blank=True, null=True)
#     recommendations = models.JSONField(default=list)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         unique_together = ('user', 'score_date')
#         ordering = ['-score_date']

#     def __str__(self):
#         return f"{self.user.email} - Optimization ({self.score_value})"

#     def calculate_total_score(self):
#         timing_weight = 0.4
#         frequency_weight = 0.3
#         consistency_weight = 0.3

#         self.score_value = (
#             self.break_timing_score * timing_weight +
#             self.break_frequency_score * frequency_weight +
#             self.break_consistency_score * consistency_weight
#         )
#         return self.score_value

#     def award_badges(self):
#         """Award badges for strong optimization habits."""
#         if self.score_value >= 85:
#             Badge.objects.get_or_create(
#                 user=self.user,
#                 badge_type='break_optimizer',
#                 defaults={
#                     'description': 'Achieved a high break optimization score',
#                     'requirements_met': {'optimization_score': self.score_value}
#                 }
#             )
