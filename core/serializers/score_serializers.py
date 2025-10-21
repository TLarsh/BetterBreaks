from rest_framework import serializers
from ..models.score_models import BreakScore, StreakScore, OptimizationScore


class BreakScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakScore
        fields = ['id', 'score_date', 'score_value', 'frequency_points', 'adherence_points',
                 'wellbeing_impact', 'break_type', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class StreakScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreakScore
        fields = ['id', 'current_streak', 'longest_streak', 'streak_period', 
                 'last_break_date', 'streak_start_date', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']


class OptimizationScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizationScore
        fields = ['id', 'score_date', 'score_value', 'break_timing_score', 
                 'break_frequency_score', 'break_consistency_score', 
                 'notes', 'recommendations', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']
