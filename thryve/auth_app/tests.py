from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import authenticate
from .models import CustomUser, CustomUserManager
from .forms import RegistrationForm


class CustomUserModelTest(TestCase):
    def test_create_user(self):
        """Test creating a regular user"""
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            company_name='Test Company'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            company_name='Admin Company'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.check_password('adminpass123'))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_user_str_method(self):
        """Test the string representation of CustomUser"""
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            company_name='Test Company'
        )
        self.assertEqual(str(user), 'test@example.com')

    def test_create_user_without_email(self):
        """Test creating user without email raises ValueError"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                email=None,
                password='testpass123',
                first_name='Test',
                last_name='User',
                company_name='Test Company'
            )


class RegistrationFormTest(TestCase):
    def test_valid_form(self):
        """Test form with valid data"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company',
            'email': 'john@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_missing_fields(self):
        """Test form with missing required fields"""
        form_data = {
            'first_name': 'John',
            # missing last_name, company_name, email, passwords
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('last_name', form.errors)
        self.assertIn('company_name', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)

    def test_duplicate_email(self):
        """Test form validation for duplicate email"""
        # Create existing user
        CustomUser.objects.create_user(
            email='existing@example.com',
            password='testpass123',
            first_name='Existing',
            last_name='User',
            company_name='Existing Company'
        )

        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company',
            'email': 'existing@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_company_name(self):
        """Test form validation for duplicate company name"""
        # Create existing user
        CustomUser.objects.create_user(
            email='existing@example.com',
            password='testpass123',
            first_name='Existing',
            last_name='User',
            company_name='Existing Company'
        )

        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Existing Company',
            'email': 'john@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('company_name', form.errors)

    def test_password_mismatch(self):
        """Test form with mismatched passwords"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company',
            'email': 'john@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass123'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_password_too_short(self):
        """Test password validation for minimum length"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company',
            'email': 'john@example.com',
            'password1': 'short',
            'password2': 'short'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_password_no_uppercase(self):
        """Test password validation for missing uppercase letter"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company',
            'email': 'john@example.com',
            'password1': 'lowercase123',
            'password2': 'lowercase123'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_password_no_lowercase(self):
        """Test password validation for missing lowercase letter"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company',
            'email': 'john@example.com',
            'password1': 'UPPERCASE123',
            'password2': 'UPPERCASE123'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_password_no_numeric(self):
        """Test password validation for missing numeric digit"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company',
            'email': 'john@example.com',
            'password1': 'PasswordOnly',
            'password2': 'PasswordOnly'
        }
        form = RegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password1', form.errors)

    def test_password_meets_all_requirements(self):
        """Test password that meets all requirements"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company',
            'email': 'john@example.com',
            'password1': 'ValidPass123',
            'password2': 'ValidPass123'
        }
        form = RegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())


class AuthenticationViewsTest(TestCase):
    def test_register_view_get(self):
        """Test GET request to register view"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_register_view_post_valid(self):
        """Test POST request to register view with valid data"""
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'company_name': 'Test Company',
            'email': 'john@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertRedirects(response, reverse('home'))

        # Check user was created
        user = CustomUser.objects.get(email='john@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.company_name, 'Test Company')

    def test_register_view_post_invalid(self):
        """Test POST request to register view with invalid data"""
        form_data = {
            'first_name': 'John',
            # missing other fields
        }
        response = self.client.post(reverse('register'), data=form_data)
        self.assertEqual(response.status_code, 200)  # Stay on same page
        self.assertTemplateUsed(response, 'accounts/register.html')

    def test_login_view_get(self):
        """Test GET request to login view"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_logout_view_get(self):
        """Test GET request to logout view"""
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/logout.html')

    def test_home_view_get(self):
        """Test GET request to home view"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'marketplace.html')

    def test_user_authentication(self):
        """Test user authentication with authenticate function"""
        # Create user
        user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            company_name='Test Company'
        )

        # Test successful authentication
        authenticated_user = authenticate(email='test@example.com', password='testpass123')
        self.assertEqual(authenticated_user, user)

        # Test failed authentication
        authenticated_user = authenticate(email='test@example.com', password='wrongpass')
        self.assertIsNone(authenticated_user)

        authenticated_user = authenticate(email='wrong@example.com', password='testpass123')
        self.assertIsNone(authenticated_user)