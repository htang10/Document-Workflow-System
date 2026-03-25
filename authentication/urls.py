from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    SignUpEndpoint,
    SignInEndpoint
)


urlpatterns = [
    path("sign-up/", SignUpEndpoint.as_view(), name="sign-up"),
    path("sign-in/", SignInEndpoint.as_view(), name="sign-in"),
    path("get-token-pair/", TokenObtainPairView.as_view(), name="get-token-pair"),
    path("get-refresh-token/", TokenRefreshView.as_view(), name="get-refresh-token"),
]