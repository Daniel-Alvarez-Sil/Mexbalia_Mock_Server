from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class OAuthSimulationTests(APITestCase):
    def test_rejects_missing_authorization_header(self):
        response = self.client.get(reverse('oauth_simulation'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_rejects_non_bearer_authorization_header(self):
        response = self.client.get(
            reverse('oauth_simulation'),
            HTTP_AUTHORIZATION='Token abc123',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_rejects_empty_bearer_token(self):
        response = self.client.get(
            reverse('oauth_simulation'),
            HTTP_AUTHORIZATION='Bearer   ',
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_accepts_non_empty_bearer_token(self):
        response = self.client.get(
            reverse('oauth_simulation'),
            HTTP_AUTHORIZATION='Bearer abc123',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['valid'], True)
