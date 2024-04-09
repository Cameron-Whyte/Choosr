from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from choosr.models import CustomUser
from rest_framework.authtoken.models import Token


class UserTest(TestCase):

    def setUp(self):
        # Initialize API client and reverse URLs to get the endpoint paths
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')

        # Sample data for valid and invalid user
        self.valid_user_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'email': 'john@example.com',
            'password1': 'ComplexInformation123!',
            'password2': 'ComplexInformation123!',
        }

        self.invalid_user_data = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01',
            'email': 'jane@example.com',
            'password1': 'password123',
            'password2': 'password321',
        }

    def create_test_user(self, user_data):
        # Create and return a CustomUser instance
        return CustomUser.objects.create_user(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            date_of_birth=user_data['date_of_birth'],
            email=user_data['email'],
            password=user_data['password1']
        )

    def test_register(self):
        # Test valid user registration
        response = self.client.post(self.register_url, self.valid_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['registered'])

        # Test invalid user registration
        response = self.client.post(self.register_url, self.invalid_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def test_login(self):
        user = self.create_test_user(self.valid_user_data)

        # Test valid login
        response = self.client.post(self.login_url, {'email': 'john@example.com', 'password': 'ComplexInformation123!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

        # Test invalid login
        response = self.client.post(self.login_url, {'email': 'john@example.com', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout(self):
        user = self.create_test_user(self.valid_user_data)
        Token.objects.create(user=user)  # Create a token for the user
        self.client.force_authenticate(user=user) # force authenticate 

        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful')