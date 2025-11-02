from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from ..models.recommendation_models import UserMetrics, BreakRecommendation
from ..services.recommendation_service import RecommendationService

User = get_user_model()

class RecommendationServiceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            full_name='Test User'
        )
        self.metrics = UserMetrics.objects.create(
            user=self.user,
            work_hours_per_week=40,
            stress_level=7,
            sleep_quality=6,
            prefers_travel=True,
            season_preference='summer',
            break_type_preference='mixed'
        )
    
    def test_generate_recommendation(self):
        # Test recommendation generation
        recommendation = RecommendationService.generate_recommendation(self.user)
        
        # Check that recommendation was created
        self.assertIsNotNone(recommendation)
        self.assertEqual(recommendation.user, self.user)
        self.assertIsNotNone(recommendation.recommended_start_date)
        self.assertIsNotNone(recommendation.recommended_end_date)
        self.assertGreater(recommendation.predicted_length_days, 0)
        self.assertIsNotNone(recommendation.message)

class RecommendationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            full_name='Test User'
        )
        self.metrics = UserMetrics.objects.create(
            user=self.user,
            work_hours_per_week=40,
            stress_level=7,
            sleep_quality=6,
            prefers_travel=True,
            season_preference='summer',
            break_type_preference='mixed'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_user_metrics(self):
        # Test getting user metrics
        url = reverse('user-metrics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['work_hours_per_week'], 40)
        self.assertEqual(response.data['stress_level'], 7)
    
    def test_create_recommendation(self):
        # Test creating a recommendation
        url = reverse('break-recommendations')
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('recommended_start_date', response.data)
        self.assertIn('recommended_end_date', response.data)
        self.assertIn('predicted_length_days', response.data)
        
        # Check that recommendation was created in database
        recommendation_id = response.data['id']
        recommendation = BreakRecommendation.objects.get(id=recommendation_id)
        self.assertEqual(recommendation.user, self.user)
        
    def test_create_recommendation_with_force(self):
        # First create a recommendation
        url = reverse('break-recommendations')
        first_response = self.client.post(url)
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        first_id = first_response.data['id']
        
        # Create another recommendation without force parameter
        # This should return the same recommendation
        second_response = self.client.post(url)
        self.assertEqual(second_response.status_code, status.HTTP_201_CREATED)
        second_id = second_response.data['id']
        self.assertEqual(first_id, second_id)  # Should be the same recommendation
        
        # Create another recommendation with force parameter
        # This should create a new recommendation
        force_url = f"{url}?force=true"
        third_response = self.client.post(force_url)
        self.assertEqual(third_response.status_code, status.HTTP_201_CREATED)
        third_id = third_response.data['id']
        self.assertNotEqual(first_id, third_id)  # Should be a different recommendation