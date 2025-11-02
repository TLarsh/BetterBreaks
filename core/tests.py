from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from .models import BreakPlan, LeaveBalance, BreakScore, StreakScore, Badge, OptimizationScore

User = get_user_model()

class SuggestedDatesViewTests(APITestCase):
    def setUp(self):
        
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='password123',
            home_location_coordinates=None  
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('suggested-dates')

    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access the view."""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_no_home_location_coordinates(self):
        """Test behavior when user has no coordinates."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("suggestions", response.data)
        self.assertGreater(len(response.data["suggestions"]), 0)


class BreakPlanGamificationTests(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            email='breaktest@example.com',
            password='password123'
        )
        
    
        self.leave_balance = LeaveBalance.objects.create(
            user=self.user,
            anual_leave_balance=20,
            anual_leave_refresh_date=datetime.now().date() + timedelta(days=365),
            already_used_balance=0
        )
        
        self.break_plan = BreakPlan.objects.create(
            user=self.user,
            leave_balance=self.leave_balance,
            startDate=datetime.now() + timedelta(days=10),
            endDate=datetime.now() + timedelta(days=15),
            description="Test vacation",
            type="vacation",
            status="planned"  
        )
        
       
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_break_plan_approval_creates_gamification_entries(self):
        """Test that approving a break plan creates appropriate gamification entries."""
       
        self.assertEqual(BreakScore.objects.filter(user=self.user).count(), 0)
        self.assertEqual(StreakScore.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Badge.objects.filter(user=self.user).count(), 0)
        
     
        self.break_plan.status = "approved"
        self.break_plan.save()
        
       
        break_scores = BreakScore.objects.filter(user=self.user)
        self.assertEqual(break_scores.count(), 1)
        self.assertEqual(break_scores[0].score_date, self.break_plan.startDate.date())
        
        # Check that a StreakScore was created/updated
        streak_scores = StreakScore.objects.filter(user=self.user)
        self.assertEqual(streak_scores.count(), 1)
        self.assertEqual(streak_scores[0].current_streak, 1) 
        
        # Check that at least one badge was awarded
        badges = Badge.objects.filter(user=self.user)
        self.assertGreater(badges.count(), 0)
        
        # Check that an OptimizationScore was created/updated
        opt_scores = OptimizationScore.objects.filter(user=self.user)
        self.assertEqual(opt_scores.count(), 1)
        
    def test_changing_to_non_approved_status_doesnt_create_entries(self):
        """Test that changing to a non-approved status doesn't create gamification entries."""
        # Change to pending (not approved)
        self.break_plan.status = "pending"
        self.break_plan.save()
        
        # Verify no break scores exist
        self.assertEqual(BreakScore.objects.filter(user=self.user).count(), 0)
        
    def test_already_approved_break_doesnt_duplicate_entries(self):
        """Test that saving an already approved break doesn't duplicate entries."""
        # First approve the break
        self.break_plan.status = "approved"
        self.break_plan.save()
        
        # Count the entries
        initial_break_score_count = BreakScore.objects.filter(user=self.user).count()
        
        # Save again without changing status
        self.break_plan.description = "Updated description"
        self.break_plan.save()
        
        # Verify no new entries were created
        self.assertEqual(BreakScore.objects.filter(user=self.user).count(), initial_break_score_count)
        
    def test_api_break_plan_approval_creates_gamification_entries(self):
        """Test that approving a break plan via API creates appropriate gamification entries."""
        # Verify no break scores exist yet
        self.assertEqual(BreakScore.objects.filter(user=self.user).count(), 0)
        self.assertEqual(StreakScore.objects.filter(user=self.user).count(), 0)
        self.assertEqual(Badge.objects.filter(user=self.user).count(), 0)
        
        # Approve the break plan via API
        url = reverse('update-break-plan', kwargs={'planId': self.break_plan.id})
        data = {
            'startDate': self.break_plan.startDate.isoformat(),
            'endDate': self.break_plan.endDate.isoformat(),
            'description': self.break_plan.description,
            'status': 'approved'  
        }
        response = self.client.put(url, data, format='json')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], True)
        self.assertEqual(response.data['data']['plan']['status'], 'approved')
        
        # Check that gamification data is included in the response
        self.assertIn('gamification', response.data['data'])
        self.assertIsNotNone(response.data['data']['gamification'])
        
        # Check that a BreakScore was created
        break_scores = BreakScore.objects.filter(user=self.user)
        self.assertEqual(break_scores.count(), 1)
        self.assertEqual(break_scores[0].score_date, self.break_plan.startDate.date())
        
        # Check that a StreakScore was created/updated
        streak_scores = StreakScore.objects.filter(user=self.user)
        self.assertEqual(streak_scores.count(), 1)
        self.assertEqual(streak_scores[0].current_streak, 1)  
        # Check that at least one badge was awarded
        badges = Badge.objects.filter(user=self.user)
        self.assertGreater(badges.count(), 0)
        
        # Check that an OptimizationScore was created/updated
        opt_scores = OptimizationScore.objects.filter(user=self.user)
        self.assertEqual(opt_scores.count(), 1)

    def test_invalid_home_location_format(self):
        """Test behavior when coordinates are invalid."""
        self.user.home_location_coordinates = "invalid,format"
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("suggestions", response.data)

    def test_valid_home_location_coordinates(self):
        """Test behavior when valid coordinates are provided."""
        self.user.home_location_coordinates = "51.5074, -0.1278"  # London
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("suggestions", response.data)
        self.assertGreater(len(response.data["suggestions"]), 0)