from datetime import date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from ..docs.recommendation_docs import (
    user_metrics_get_docs,
    user_metrics_post_docs,
    break_recommendation_get_docs,
    break_recommendation_post_docs,
    break_recommendation_detail_get_docs,
    break_recommendation_detail_patch_docs,
    convert_to_break_plan_docs
)
from ..models.recommendation_models import UserMetrics, BreakRecommendation
from ..serializers.recommendation_serializers import UserMetricsSerializer, BreakRecommendationSerializer
from ..services.recommendation_service import RecommendationService
from ..services.user_metrics_service import UserMetricsService
from ..ml_engine.breaks_engine import generate_break_recommendation


class UserMetricsView(APIView):
    """API view for managing user metrics"""
    permission_classes = [permissions.IsAuthenticated]

    @user_metrics_get_docs
    def get(self, request):
        """Get user metrics"""
        try:
            metrics = UserMetrics.objects.get(user=request.user)
            serializer = UserMetricsSerializer(metrics)
            return Response(serializer.data)
        except UserMetrics.DoesNotExist:
            return Response({"detail": "User metrics not found"}, status=status.HTTP_404_NOT_FOUND)

    # @user_metrics_post_docs
    # def post(self, request):
    #     """Create or update user metrics"""
    #     serializer = UserMetricsSerializer(data=request.data, context={'request': request})
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request):
        metrics = UserMetricsService.build(request.user)
        serializer = UserMetricsSerializer(metrics)
        return Response(serializer.data, status=200)



class BreakRecommendationView(APIView):
    """API view for generating and managing break recommendations"""
    permission_classes = [permissions.IsAuthenticated]

    @break_recommendation_get_docs
    def get(self, request):
        """Get user's break recommendations"""
        recommendations = BreakRecommendation.objects.filter(user=request.user).order_by('-created_at')
        serializer = BreakRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)

    @break_recommendation_post_docs
    def post(self, request):
        """Generate a new break recommendation"""
        # Check if force parameter is provided
        force_new = request.query_params.get('force', 'false').lower() == 'true'

        if force_new:
            # If force is true, bypass the recent recommendation check in the service
            try:
                user_metrics = UserMetrics.objects.get(user=request.user)
                user_input = RecommendationService.get_user_input_dict(user_metrics)
                recommendation_data = generate_break_recommendation(user_input)

                recommendation = BreakRecommendation.objects.create(
                    user=request.user,
                    recommended_start_date=date.fromisoformat(recommendation_data['recommended_start_date']),
                    recommended_end_date=date.fromisoformat(recommendation_data['recommended_end_date']),
                    predicted_length_days=recommendation_data['predicted_length_days'],
                    recommended_season=recommendation_data['recommended_season'],
                    message=recommendation_data['message']
                )
            except Exception as e:
                return Response({"detail": f"Failed to generate recommendation: {str(e)}"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # Use the service which includes the recent recommendation check
            recommendation = RecommendationService.generate_recommendation(request.user)

        if recommendation:
            serializer = BreakRecommendationSerializer(recommendation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"detail": "Failed to generate recommendation"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BreakRecommendationDetailView(APIView):
    """API view for managing a specific break recommendation"""
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        """Get recommendation object"""
        try:
            return BreakRecommendation.objects.get(pk=pk, user=user)
        except BreakRecommendation.DoesNotExist:
            return None

    @break_recommendation_detail_get_docs
    def get(self, request, pk):
        """Get a specific recommendation"""
        recommendation = self.get_object(pk, request.user)
        if recommendation:
            serializer = BreakRecommendationSerializer(recommendation)
            return Response(serializer.data)
        return Response({"detail": "Recommendation not found"}, status=status.HTTP_404_NOT_FOUND)

    @break_recommendation_detail_patch_docs
    def patch(self, request, pk):
        """Update a specific recommendation (mark as viewed/accepted)"""
        recommendation = self.get_object(pk, request.user)
        if not recommendation:
            return Response({"detail": "Recommendation not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BreakRecommendationSerializer(recommendation, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@convert_to_break_plan_docs
def convert_to_break_plan(request, pk):
    """Convert a recommendation to a break plan"""
    try:
        recommendation = BreakRecommendation.objects.get(pk=pk, user=request.user)
    except BreakRecommendation.DoesNotExist:
        return Response({"detail": "Recommendation not found"}, status=status.HTTP_404_NOT_FOUND)

    # Convert recommendation to break plan
    break_plan = RecommendationService.convert_recommendation_to_break_plan(recommendation, request.user)

    # Mark recommendation as accepted
    recommendation.is_accepted = True
    recommendation.save()

    # Return break plan ID
    return Response({"break_plan_id": break_plan.id}, status=status.HTTP_201_CREATED)