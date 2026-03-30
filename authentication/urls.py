from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    SignUpEndpoint,
    LoginEndpoint,
    LogoutEndpoint,
)


urlpatterns = [
    path("signup/", SignUpEndpoint.as_view(), name="signup"),
    path("login/", LoginEndpoint.as_view(), name="login"),
    path("logout/", LogoutEndpoint.as_view(), name="logout"),
    path("get-access-token/", TokenRefreshView.as_view(), name="get-access-token"),
]