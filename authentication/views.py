from rest_framework import status
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    SignUpSerializer,
    LoginSerializer,
)
from .utils import update_user_login_metadata


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