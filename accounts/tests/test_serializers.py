from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.serializers import (
    LoginSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
)


User = get_user_model()


class LoginSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )

    def test_login_with_email(self):
        """Test login with email"""
        data = {"username_or_email": "test@example.com", "password": "testpass123"}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertIn("access", serializer.validated_data)
        self.assertIn("refresh", serializer.validated_data)

    def test_login_with_username(self):
        """Test login with username"""
        data = {"username_or_email": "testuser", "password": "testpass123"}
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {"username_or_email": "test@example.com", "password": "wrongpassword"}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        data = {
            "username_or_email": "nonexistent@example.com",
            "password": "testpass123",
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()

        data = {"username_or_email": "test@example.com", "password": "testpass123"}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_login_missing_fields(self):
        """Test login with missing fields"""
        data = {"username_or_email": "test@example.com"}
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)


class UserRegistrationSerializerTest(TestCase):
    def test_valid_user_registration(self):
        """Test valid user registration"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
            "first_name": "John",
            "last_name": "Doe",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Doe")
        self.assertTrue(user.check_password("newpass123"))

    def test_password_mismatch(self):
        """Test registration with password mismatch"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "differentpass",
            "first_name": "John",
            "last_name": "Doe",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password_confirm", serializer.errors)

    def test_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="testpass123",
        )

        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_short_password(self):
        """Test registration with short password"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "short",
            "password_confirm": "short",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("password", serializer.errors)

    def test_missing_required_fields(self):
        """Test registration with missing required fields"""
        data = {
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("username", serializer.errors)

    def test_password_confirm_not_saved(self):
        """Test that password_confirm is not saved to database"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpass123",
            "password_confirm": "newpass123",
        }
        serializer = UserRegistrationSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertFalse(hasattr(user, "password_confirm"))


class UserProfileSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            first_name="John",
            last_name="Doe",
        )

    def test_user_profile_serialization(self):
        """Test user profile serialization includes correct fields"""
        serializer = UserProfileSerializer(self.user)
        expected_fields = {
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
        }
        self.assertEqual(set(serializer.data.keys()), expected_fields)
        self.assertEqual(serializer.data["email"], "test@example.com")
        self.assertEqual(serializer.data["username"], "testuser")

    def test_update_user_profile(self):
        """Test updating user profile"""
        data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
        }
        serializer = UserProfileSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()
        self.assertEqual(updated_user.username, "updateduser")
        self.assertEqual(updated_user.email, "updated@example.com")
        self.assertEqual(updated_user.first_name, "Jane")
        self.assertEqual(updated_user.last_name, "Smith")

    def test_readonly_fields(self):
        """Test that readonly fields cannot be updated"""
        original_date_joined = self.user.date_joined
        original_id = self.user.id

        data = {"id": 999, "date_joined": "2025-01-01T00:00:00Z"}
        serializer = UserProfileSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())

        updated_user = serializer.save()
        self.assertEqual(updated_user.id, original_id)
        self.assertEqual(updated_user.date_joined, original_date_joined)


class ChangePasswordSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="oldpass123"
        )

    def test_valid_password_change(self):
        """Test valid password change"""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        serializer = ChangePasswordSerializer(
            data=data, context={"request": type("obj", (object,), {"user": self.user})}
        )
        self.assertTrue(serializer.is_valid())

    def test_wrong_old_password(self):
        """Test password change with wrong old password"""
        data = {
            "old_password": "wrongoldpass",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }
        serializer = ChangePasswordSerializer(
            data=data, context={"request": type("obj", (object,), {"user": self.user})}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("old_password", serializer.errors)

    def test_new_password_mismatch(self):
        """Test password change with new password mismatch"""
        data = {
            "old_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "differentpass",
        }
        serializer = ChangePasswordSerializer(
            data=data, context={"request": type("obj", (object,), {"user": self.user})}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password_confirm", serializer.errors)

    def test_short_new_password(self):
        """Test password change with short new password"""
        data = {
            "old_password": "oldpass123",
            "new_password": "short",
            "new_password_confirm": "short",
        }
        serializer = ChangePasswordSerializer(
            data=data, context={"request": type("obj", (object,), {"user": self.user})}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password", serializer.errors)

    def test_missing_fields(self):
        """Test password change with missing fields"""
        data = {"old_password": "oldpass123", "new_password": "newpass123"}
        serializer = ChangePasswordSerializer(
            data=data, context={"request": type("obj", (object,), {"user": self.user})}
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("new_password_confirm", serializer.errors)
