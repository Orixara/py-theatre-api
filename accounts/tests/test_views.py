from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class RegisterViewTest(APITestCase):
    def test_register_user_success(self):
        """Test successful user registration"""
        url = reverse("accounts:register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "John",
            "last_name": "Doe",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_register_user_password_mismatch(self):
        """Test registration with password mismatch"""
        url = reverse("accounts:register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "differentpass",
            "first_name": "John",
            "last_name": "Doe",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password_confirm", response.data)

    def test_register_user_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="testpass123",
        )

        url = reverse("accounts:register")
        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_missing_fields(self):
        """Test registration with missing required fields"""
        url = reverse("accounts:register")
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_register_user_short_password(self):
        """Test registration with short password"""
        url = reverse("accounts:register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "short",
            "password_confirm": "short",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_view_throttling(self):
        """Test that register view has throttling applied"""
        url = reverse("accounts:register")
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LoginViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_login_with_email(self):
        """Test login with email"""
        url = reverse("accounts:login")
        data = {"username_or_email": "test@example.com", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_with_username(self):
        """Test login with username"""
        url = reverse("accounts:login")
        data = {"username_or_email": "testuser", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse("accounts:login")
        data = {"username_or_email": "test@example.com", "password": "wrongpassword"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        url = reverse("accounts:login")
        data = {
            "username_or_email": "nonexistent@example.com",
            "password": "testpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()

        url = reverse("accounts:login")
        data = {"username_or_email": "test@example.com", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        url = reverse("accounts:login")
        data = {"username_or_email": "test@example.com"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_login_view_throttling(self):
        """Test that login view has throttling applied"""
        url = reverse("accounts:login")
        data = {"username_or_email": "test@example.com", "password": "testpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserProfileViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

    def authenticate_user(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_user_profile_authenticated(self):
        """Test retrieving user profile when authenticated"""
        self.authenticate_user()
        url = reverse("accounts:user-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "test@example.com")
        self.assertEqual(response.data["username"], "testuser")
        self.assertEqual(response.data["first_name"], "John")
        self.assertEqual(response.data["last_name"], "Doe")

    def test_get_user_profile_unauthenticated(self):
        """Test retrieving user profile when not authenticated"""
        url = reverse("accounts:user-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_user_profile_authenticated(self):
        """Test updating user profile when authenticated"""
        self.authenticate_user()
        url = reverse("accounts:user-profile")
        data = {"first_name": "Jane", "last_name": "Smith"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Jane")
        self.assertEqual(self.user.last_name, "Smith")

    def test_update_user_email(self):
        """Test updating user email"""
        self.authenticate_user()
        url = reverse("accounts:user-profile")
        data = {"email": "newemail@example.com"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")

    def test_update_readonly_fields(self):
        """Test that readonly fields cannot be updated"""
        self.authenticate_user()
        url = reverse("accounts:user-profile")
        original_id = self.user.id
        original_date_joined = self.user.date_joined

        data = {"id": 999, "date_joined": "2025-01-01T00:00:00Z"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.id, original_id)
        self.assertEqual(self.user.date_joined, original_date_joined)

    def test_profile_response_fields(self):
        """Test that profile response contains expected fields"""
        self.authenticate_user()
        url = reverse("accounts:user-profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_fields = {
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
        }
        self.assertEqual(set(response.data.keys()), expected_fields)


class ChangePasswordViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpass123"
        )

    def authenticate_user(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_change_password_success(self):
        """Test successful password change"""
        self.authenticate_user()
        url = reverse("accounts:change-password")
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Password updated successfully", response.data["message"])

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpass123"))
        self.assertFalse(self.user.check_password("oldpass123"))

    def test_change_password_unauthenticated(self):
        """Test password change when not authenticated"""
        url = reverse("accounts:change-password")
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.authenticate_user()
        url = reverse("accounts:change-password")
        data = {
            "old_password": "wrongoldpass",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("old_password", response.data)

    def test_change_password_mismatch(self):
        """Test password change with new password mismatch"""
        self.authenticate_user()
        url = reverse("accounts:change-password")
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "differentpass",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password_confirm", response.data)

    def test_change_password_short_new_password(self):
        """Test password change with short new password"""
        self.authenticate_user()
        url = reverse("accounts:change-password")
        data = {
            "old_password": "oldpass123",
            "new_password": "short",
            "new_password_confirm": "short",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_missing_fields(self):
        """Test password change with missing fields"""
        self.authenticate_user()
        url = reverse("accounts:change-password")
        data = {"old_password": "oldpass123", "new_password": "newpass123"}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("new_password_confirm", response.data)

    def test_change_password_throttling(self):
        """Test that change password view has throttling applied"""
        self.authenticate_user()
        url = reverse("accounts:change-password")
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_only_post_method(self):
        """Test that change password only accepts POST method"""
        self.authenticate_user()
        url = reverse("accounts:change-password")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.put(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.patch(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class AccountsPermissionTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_public_views_no_auth_required(self):
        """Test that register and login views don't require authentication"""
        register_url = reverse("accounts:register")
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }
        response = self.client.post(register_url, register_data, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        login_url = reverse("accounts:login")
        login_data = {
            "username_or_email": "test@example.com",
            "password": "testpass123",
        }
        response = self.client.post(login_url, login_data, format="json")
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_protected_views_require_auth(self):
        """Test that profile and change password views require authentication"""
        profile_url = reverse("accounts:user-profile")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        change_password_url = reverse("accounts:change-password")
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        response = self.client.post(change_password_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
