from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import Http404
from datetime import date, timedelta
from ..serializers.badge_serializers import BadgeSerializer
from ..models.break_models import BreakScore
from ..models.badge_models import Badge
from ..docs.badge_docs import (
    badge_list,
    badge_retrieve,
    badge_update,
    badge_delete,
    badge_eligibility
)




########### BADGE ENDPOINT ############
###############################


class BadgeListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    @badge_list
    def get(self, request):
        """Get all badges for the current user"""
        badges = Badge.objects.filter(user=request.user)
        serializer = BadgeSerializer(badges, many=True)
        return Response(serializer.data)
    
    # @badge_create
    # def post(self, request):
    #     """Create a new badge"""
    #     serializer = BadgeSerializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(user=request.user)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

class BadgeDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Badge.objects.get(pk=pk, user=self.request.user)
        except Badge.DoesNotExist:
            raise Http404
    
    @badge_retrieve
    def get(self, request, pk):
        """Get a specific badge"""
        badge = self.get_object(pk)
        serializer = BadgeSerializer(badge)
        return Response(serializer.data)
    
    @badge_update
    def put(self, request, pk):
        """Update a specific badge"""
        badge = self.get_object(pk)
        serializer = BadgeSerializer(badge, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @badge_delete
    def delete(self, request, pk):
        """Delete a specific badge"""
        badge = self.get_object(pk)
        badge.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class BadgeEligibilityView(APIView):
    permission_classes = [IsAuthenticated]
    
    @badge_eligibility
    def post(self, request):
        """Check if user is eligible for new badges and award them"""
        user = request.user
        new_badges = []
        
        # Check for Weekend Breaker badge
        weekend_breaks = BreakScore.objects.filter(
            user=user,
            break_type='weekend',
            score_date__gte=date.today() - timedelta(days=30)
        ).count()
        
        if weekend_breaks >= 8 and not Badge.objects.filter(user=user, badge_type='weekend_breaker', level='bronze').exists():
            badge = Badge.objects.create(
                user=user,
                badge_type='weekend_breaker',
                level='bronze',
                description="Took breaks on 8 weekends in a month",
                requirements_met={"weekend_breaks": weekend_breaks}
            )
            new_badges.append(badge)
            user.total_badges += 1
            user.save()
        
        # More checks still coming here...
        
        serializer = BadgeSerializer(new_badges, many=True)
        return Response(serializer.data)