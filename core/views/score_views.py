from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import Http404
from datetime import date
from ..serializers.score_serializers import OptimizationScoreSerializer, StreakScoreSerializer, BreakScoreSerializer
from ..models.score_models import OptimizationScore, StreakScore, BreakScore
from ..models.preference_models import BreakPreferences
from ..models.working_pattern_models import WorkingPattern
from ..models.break_models import BreakScore
from ..docs.score_docs import (
    optimization_list,
    optimization_create,
    optimization_retrieve,
    optimization_update,
    optimization_delete,
    optimization_calculate,
    streak_list,
    streak_create,
    streak_retrieve,
    streak_update,
    streak_delete,
    score_summary
)

from ..serializers.score_serializers import StreakScoreSerializer


########STREAK BREAK ENDPOINT ###########################
############################################


class StreakListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @streak_list
    def get(self, request):
        """Get all streak scores for the current user"""
        streaks = StreakScore.objects.filter(user=request.user)
        serializer = StreakScoreSerializer(streaks, many=True)
        return Response(serializer.data)
    
    # @streak_create
    # def post(self, request):
    #     """Create a new streak score"""
    #     serializer = StreakScoreSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=request.user)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

class StreakDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return StreakScore.objects.get(pk=pk, user=self.request.user)
        except StreakScore.DoesNotExist:
            raise Http404
    
    @streak_retrieve
    def get(self, request, pk):
        """Get a specific streak score"""
        streak = self.get_object(pk)
        serializer = StreakScoreSerializer(streak)
        return Response(serializer.data)
    
    # @streak_update
    # def put(self, request, pk):
    #     """Update a specific streak score"""
    #     streak = self.get_object(pk)
    #     serializer = StreakScoreSerializer(streak, data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save()
    #     return Response(serializer.data)
    
    @streak_delete
    def delete(self, request, pk):
        """Delete a specific streak score"""
        streak = self.get_object(pk)
        streak.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    



class ScoreSummaryView(APIView):
    permission_classes = [IsAuthenticated]
    
    @score_summary
    def get(self, request):
        """Get user's current break score and streak information"""
        user = request.user
        
        # Get latest break scores
        recent_breaks = BreakScore.objects.filter(user=user).order_by('-score_date')[:5]
        break_serializer = BreakScoreSerializer(recent_breaks, many=True)
        
        # Get streak information
        streaks = StreakScore.objects.filter(user=user)
        streak_serializer = StreakScoreSerializer(streaks, many=True)
        
        # Get optimization score
        optimization = OptimizationScore.objects.filter(user=user).order_by('-score_date').first()
        optimization_serializer = OptimizationScoreSerializer(optimization) if optimization else None
        
        return Response({
            "total_break_score": user.total_break_score,
            "highest_streak": user.highest_streak,
            "recent_breaks": break_serializer.data,
            "streaks": streak_serializer.data,
            "optimization": optimization_serializer.data if optimization else None,
        })

############ OPTIMISATION ENDPINT ############
############################################ In core/views.py

class OptimizationListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @optimization_list
    def get(self, request):
        """Get all optimization scores for the current user"""
        optimization_scores = OptimizationScore.objects.filter(user=request.user)
        serializer = OptimizationScoreSerializer(optimization_scores, many=True)
        return Response(serializer.data)
    
    # @optimization_create
    # def post(self, request):
    #     """Create a new optimization score"""
    #     serializer = OptimizationScoreSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=request.user)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

class OptimizationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return OptimizationScore.objects.get(pk=pk, user=self.request.user)
        except OptimizationScore.DoesNotExist:
            raise Http404
    
    @optimization_retrieve
    def get(self, request, pk):
        """Get a specific optimization score"""
        optimization = self.get_object(pk)
        serializer = OptimizationScoreSerializer(optimization)
        return Response(serializer.data)
    
    @optimization_update
    def put(self, request, pk):
        """Update a specific optimization score"""
        optimization = self.get_object(pk)
        serializer = OptimizationScoreSerializer(optimization, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @optimization_delete
    def delete(self, request, pk):
        """Delete a specific optimization score"""
        optimization = self.get_object(pk)
        optimization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OptimizationCalculateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @optimization_calculate
    def post(self, request):
        """Calculate optimization score based on user's break patterns"""
        user = request.user
        
        # Get user's break preferences and working pattern
        try:
            preferences = BreakPreferences.objects.get(user=user)
            pattern = WorkingPattern.objects.get(user=user)
        except (BreakPreferences.DoesNotExist, WorkingPattern.DoesNotExist):
            return Response({"error": "User preferences or working pattern not set"}, status=400)
        
        # Calculate component scores based on user data
        break_timing_score = self._calculate_timing_score(user, pattern, preferences)
        break_frequency_score = self._calculate_frequency_score(user, preferences)
        break_consistency_score = self._calculate_consistency_score(user)
        
        # Create or update optimization score
        score, created = OptimizationScore.objects.get_or_create(
            user=user,
            score_date=date.today(),
            defaults={
                'break_timing_score': break_timing_score,
                'break_frequency_score': break_frequency_score,
                'break_consistency_score': break_consistency_score,
                'recommendations': self._generate_recommendations(break_timing_score, break_frequency_score, break_consistency_score)
            }
        )
        
        if not created:
            score.break_timing_score = break_timing_score
            score.break_frequency_score = break_frequency_score
            score.break_consistency_score = break_consistency_score
            score.recommendations = self._generate_recommendations(break_timing_score, break_frequency_score, break_consistency_score)
            score.save()
        
        # Calculate total score
        total_score = score.calculate_total_score()
        score.save()
        
        # Update user's last optimization score
        user.last_optimization_score = total_score
        user.save()
        
        serializer = self.get_serializer(score)
        return Response(serializer.data)
    
    def _calculate_timing_score(self, user, pattern, preferences):
        # Implementation of timing score calculation
        pass
    
    def _calculate_frequency_score(self, user, preferences):
        # Implementation of frequency score calculation
        pass
    
    def _calculate_consistency_score(self, user):
        # Implementation of consistency score calculation
        pass
    
    def _generate_recommendations(self, timing_score, frequency_score, consistency_score):
        # Generate personalized recommendations
        recommendations = []
        
        if timing_score < 60:
            recommendations.append("Try taking breaks at more optimal times during your work day")
        
        if frequency_score < 60:
            recommendations.append("Consider increasing your break frequency to match your preferences")
        
        if consistency_score < 60:
            recommendations.append("Work on maintaining a consistent break schedule")
        
        return recommendations