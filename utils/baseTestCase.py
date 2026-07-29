from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import TestCase
from account.models import User

class BaseTestCase(TestCase):
    def setUp(self):
        # Create a user and log them in
        self.user = User.objects.create(mobile="9876543210")
        self.login_url = reverse('auth-register-or-login')
        
        data = {'mobile': '1234567890', 'otp': '1234'}
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['data'])
        self.token = response.data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def tearDown(self):
        self.client.logout()

class ApiBaseTestCase(APITestCase):
    def setUp(self):
        # Create a user and log them in
        self.user = User.objects.create(mobile="9876543210")
        self.login_url = reverse('auth-register-or-login')
        
        data = {'mobile': '1234567890', 'otp': '1234'}
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data['data'])
        self.token = response.data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
