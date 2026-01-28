from django.urls import path

from .views import (  # Use o nome exato da sua classe de View
    LoginView,
    LogoutView,
    RefreshTokenView,
    SignUpView,
)

app_name = "users"

urlpatterns = [
    path("register/", SignUpView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh-token/", RefreshTokenView.as_view(), name="refresh_token"),
]
