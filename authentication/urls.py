from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    SignUpEndpoint,
    LoginEndpoint
)


urlpatterns = [
    path("signup/", SignUpEndpoint.as_view(), name="signup"),
    path("login/", LoginEndpoint.as_view(), name="login"),
    path("get-token-pair/", TokenObtainPairView.as_view(), name="get-token-pair"),
    path("get-refresh-token/", TokenRefreshView.as_view(), name="get-refresh-token"),
]