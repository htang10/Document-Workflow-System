from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.exceptions import (
    EmailVerificationError,
    AlreadyVerifiedError,
)
from authentication.serializers import (
    SignUpSerializer,
    LoginSerializer,
    LogoutSerializer,
    ResendVerificationSerializer,
)
from authentication.mailing import (
    handle_email_verification,
    resend_verification_email,
    verify_token,
)
from authentication.utils import update_user_login_metadata


class SignUpEndpoint(GenericAPIView):
    """Password-based sign-up endpoint"""
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        try:
            handle_email_verification(user)
        except EmailVerificationError:
            return Response({
                "message": "Account created but verification email failed to send.",
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": f"Account created. A verification email has been sent to {user.email}.",
        }, status=status.HTTP_201_CREATED)


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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        refresh = serializer.validated_data["refresh"]

        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmailEndpoint(APIView):
    """Endpoint for verifying user email"""
    permission_classes = [AllowAny]

    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response({
                "message": "Token is required."
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
        email = serializer.validated_data["email"]

        try:
            resend_verification_email(email)
        except AlreadyVerifiedError:
            return Response({
                "message": "This account is already verified."
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "success": f"A verification email has been sent to {email}."
        }, status=status.HTTP_200_OK)
