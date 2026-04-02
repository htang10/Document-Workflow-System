from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from authentication.serializers import (
    SignUpSerializer,
    LoginSerializer,
    LogoutSerializer,
    ResendVerificationSerializer
)
from authentication.services.mailing import (
    handle_email_verification,
    verify_token,
)
from authentication.services.user import (
    get_user_by_refresh_token,
    update_user_login_metadata,
    update_user_logout_metadata,
)


class SignUpEndpoint(CreateAPIView):
    """Password-based sign-up endpoint"""
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]


class LoginEndpoint(GenericAPIView):
    """Password-based login endpoint"""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        # update tracking fields
        user = update_user_login_metadata(user, request)

        # Generate refresh and access token
        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "email": user.email,
                "display_name": user.display_name,
            }
        }, status=status.HTTP_200_OK)


class LogoutEndpoint(GenericAPIView):
    """Logout endpoint for all auth methods"""
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        try:
            # Retrieve the owner
            user = get_user_by_refresh_token(refresh_token)
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({
                "error": "Token is invalid or already blacklisted."
            }, status=status.HTTP_400_BAD_REQUEST)

        updated_user = update_user_logout_metadata(user, request)

        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmailEndpoint(APIView):
    """Endpoint for verifying user email"""
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({
                "error": "Token is required."
            },status=status.HTTP_400_BAD_REQUEST)

        verify_token(token)

        return Response({
            "message": "Email verified successfully."
        }, status=status.HTTP_200_OK)


class ResendVerificationEndpoint(GenericAPIView):
    """Endpoint for resending verification email"""
    serializer_class = ResendVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        handle_email_verification(user)

        return Response({
            "message": f"A verification email has been sent to {user.email}."
        }, status=status.HTTP_200_OK)

