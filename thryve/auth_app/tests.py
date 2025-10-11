from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            company_name='Test Company'
        )

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_user_can_login_with_correct_credentials(self):
        response = self.client.post('/login/', {
            'username': 'testuser@example.com',
            'password': 'testpassword123'
        })
        self.assertEqual(response.status_code, 302)

    def test_user_cannot_login_with_wrong_credentials(self):
        response = self.client.post('/login/', {
            'username': 'testuser@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_registration_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_user_registration_creates_new_account(self):
        response = self.client.post('/register/', {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'company_name': 'New Company',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        })
        self.assertEqual(response.status_code, 302)

    def test_logout_redirects_to_login(self):
        self.client.login(username='testuser@example.com', password='testpassword123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)