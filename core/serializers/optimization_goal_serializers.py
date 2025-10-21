from rest_framework import serializers
from ..models.optimization_goal_models import OptimizationGoal

# ======= OPTIMIZATION-GOAL-SERILIZER ========
class OptimizationGoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizationGoal
        fields = '__all__'
        read_only_fields = ('user',)
