from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from accounts.services import AuthenticationService


User = get_user_model()


class AuthenticationServiceTest(TestCase):
    def setUp(self):
        self.active_user = User.objects.create_user(
            username="activeuser", email="active@example.com", password="testpass123"
        )
        self.inactive_user = User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="testpass123",
        )
        self.inactive_user.is_active = False
        self.inactive_user.save()

    def test_authenticate_user_with_email_success(self):
        """Test successful authentication with email"""
        user = AuthenticationService.authenticate_user(
            "active@example.com", "testpass123"
        )
        self.assertEqual(user, self.active_user)

    def test_authenticate_user_with_username_success(self):
        """Test successful authentication with username"""
        user = AuthenticationService.authenticate_user(
            "activeuser",
            "testpass123"
        )
        self.assertEqual(user, self.active_user)

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            AuthenticationService.authenticate_user(
                "active@example.com", "wrongpassword"
            )
        self.assertIn("Invalid credentials", str(context.exception))

    def test_authenticate_user_nonexistent_email(self):
        """Test authentication with nonexistent email raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            AuthenticationService.authenticate_user(
                "nonexistent@example.com", "testpass123"
            )
        self.assertIn("Invalid credentials", str(context.exception))

    def test_authenticate_user_nonexistent_username(self):
        """Test authentication with nonexistent username raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            AuthenticationService.authenticate_user(
                "nonexistentuser",
                "testpass123"
            )
        self.assertIn("Invalid credentials", str(context.exception))

    def test_authenticate_user_inactive_user(self):
        """Test authentication with inactive user raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            AuthenticationService.authenticate_user(
                "inactive@example.com", "testpass123"
            )
        self.assertIn("User account is disabled", str(context.exception))

    def test_authenticate_user_empty_identifier(self):
        """Test authentication with empty identifier raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            AuthenticationService.authenticate_user("", "testpass123")
        self.assertIn("Both fields are required", str(context.exception))

    def test_authenticate_user_empty_password(self):
        """Test authentication with empty password raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            AuthenticationService.authenticate_user("active@example.com", "")
        self.assertIn("Both fields are required", str(context.exception))

    def test_authenticate_user_both_empty(self):
        """Test authentication with both fields empty raises ValidationError"""
        with self.assertRaises(ValidationError) as context:
            AuthenticationService.authenticate_user("", "")
        self.assertIn("Both fields are required", str(context.exception))

    def test_authenticate_user_special_characters_in_password(self):
        """Test authentication with special characters in password"""
        special_user = User.objects.create_user(
            username="specialuser",
            email="special@example.com",
            password="pass!@#$%^&*()",
        )

        user = AuthenticationService.authenticate_user(
            "special@example.com", "pass!@#$%^&*()"
        )
        self.assertEqual(user, special_user)
