from rest_framework import serializers
from rest_framework.authentication import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from authentication.models import User


class SignUpSerializer(serializers.ModelSerializer):
    """
    Serializer for sign-up

    Creates new user account if email has not been registered yet
    Hashes password before storing user in db
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
    Serializer for login

    Checks for existing email and correct password
    """
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"}
    )

    def validate(self, data):
        normalized_email = data["email"].lower().strip()
        user = authenticate(
            username=normalized_email,
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError({"error": "Email does not exist or incorrect password."})

        user_obj = User.objects.get(email=normalized_email)
        if not user_obj.email_verified_at:
            raise serializers.ValidationError({"error": "Email not verified yet."})

        data["user"] = user
        return data


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logout

    Blacklists refresh token after logout
    """
    refresh = serializers.CharField()

    def validate(self, data):
        try:
            token = RefreshToken(data["refresh"])
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError("Token is invalid or already blacklisted.")
        return data


class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer for resending verification email

    Only send verification to an existing account
    """
    email = serializers.EmailField(max_length=255)

    def validate_email(self, value):
        email = value.lower().strip()
        existing_user = User.objects.filter(email=email).exists()

        if not existing_user:
            raise serializers.ValidationError("User with this email does not exist.")

        return email
