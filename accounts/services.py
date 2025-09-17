from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class AuthenticationService:
    @staticmethod
    def authenticate_user(identifier: str, password: str):
        if not identifier or not password:
            raise serializers.ValidationError("Both fields are required.")

        user = User.objects.filter(email=identifier).first()
        if not user:
            user = User.objects.filter(username=identifier).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        return user


class UserValidationService:
    @staticmethod
    def validate_email_uniqueness(email: str, exclude_user_id: int = None):
        queryset = User.objects.filter(email=email)
        if exclude_user_id:
            queryset = queryset.exclude(id=exclude_user_id)

        if queryset.exists():
            raise serializers.ValidationError("User with this email already exists.")
        return email