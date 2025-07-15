from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class SuggestedDatesViewTests(APITestCase):
    def setUp(self):
        # Create and authenticate a test user
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='password123',
            home_location_coordinates=None  # Default no location
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('suggested-dates')  # Make sure this matches your URL name

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