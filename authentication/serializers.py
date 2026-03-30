from rest_framework import serializers
from rest_framework.authentication import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import User


class SignUpSerializer(serializers.ModelSerializer):
    """
    Serializer for registering new users.

    Handles email and password validation, and user creation.
    """
    class Meta:
        model = User
        fields = ["email", "password", "display_name", "created_at", "updated_at"]
        read_only_fields = ["display_name", "created_at", "updated_at"]
        extra_kwargs = {
            "password": {
                "min_length": 8,
                "write_only": True,
                "style": {"input_type": "password"}
            }
        }

    def validate_email(self, value):
        email = value.lower().strip()
        existing_user = User.objects.filter(email=email).exists()

        if existing_user:
            raise serializers.ValidationError("User with this email already exists.")

        return email

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login.

    Handles email and password validation, and authentication.
    """
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, data):
        user = authenticate(
            username=data["email"].lower().strip(),
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError({"error": "Email does not exist or incorrect password."})

        data["user"] = user
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, data):
        try:
            token = RefreshToken(data["refresh"])
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError("Token is invalid or already blacklisted.")
        return data


