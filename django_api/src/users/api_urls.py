from django.urls import path

from .views import LoginView, SignUpView  # Use o nome exato da sua classe de View

app_name = "users"

urlpatterns = [
    path("register/", SignUpView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]
