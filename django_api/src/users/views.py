from operator import ge
from pickle import TRUE
from typing import TYPE_CHECKING

from django.conf import settings
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from users.exceptions import UnauthorizedAccessException
from users.response_handler import APIResponse
from users.serializers import (
    LoginSerializer,
    RefreshTokenSerializer,
    RegisterSerializer,
)

if TYPE_CHECKING:
    from rest_framework.request import Request

class SignUpView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    POST /api/auth/register/
    {
        "email": "user@example.com",
        "username": "username",
        "password": "password123",
        "plan_tier": "FREE"
    }
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Registra novo usuário"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = APIResponse(
            status_code=status.HTTP_201_CREATED,
            message="User registered successfully",
            data={
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "plan": user.plan,
                "user_type": user.user_type,
                "created_at": user.created_at.isoformat(),
            },
            error=None,
            trace_id=None,
            timestamp=None,
        )

        return Response(
            data=response.to_dict(),
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.CreateAPIView):
    """
    API endpoint for user login.

    POST /api/auth/login/
    {
        "email": "user@example.com",
        "password": "password123",
        "remember_me": true
    }
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Autentica usuário"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        response_data = APIResponse(
            status_code=status.HTTP_200_OK,
            message="User logged in successfully",
            data={
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "access_token": user.jwt_access,
                "refresh_token": user.jwt_refresh,
            },
            error=None,
            trace_id=None,
            timestamp=None,
        )

        response = Response(
            data=response_data.to_dict(),
            status=status.HTTP_200_OK,
        )

        if request.data.get("remember_me", TRUE):

            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=user.jwt_refresh,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],  # 7 days
            )

        else:
            pass

        response.set_cookie(
            key=settings.SIMPLE_JWT['AUTH_COOKIE'],
            value=user.jwt_access,
            httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
            secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
            samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
            max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],  # 24 hours
        )

        return response

class LogoutView(generics.GenericAPIView):
    """
    API endpoint for user logout.

    POST /api/auth/logout/
    """
    serializer_class = None
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Desloga o usuário"""

        response_data = APIResponse(
            status_code=status.HTTP_200_OK,
            message="User logged out successfully",
            data=None,
            error=None,
            trace_id=None,
            timestamp=None,
        )

        response = Response(
            data=response_data.to_dict(),
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        response.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])

        return response

class RefreshTokenView(generics.GenericAPIView):
    """
    API endpoint for refreshing JWT tokens.

    POST /api/auth/refresh-token/
    {
        "refresh_token": "your_refresh_token_here"
    }
    """

    serializer_class = RefreshTokenSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Refresca o token de acesso"""
        refresh_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])

        if not refresh_token:
            error_msg = "Refresh token is required"
            raise UnauthorizedAccessException(error_msg) from None
        serializer = self.get_serializer(data={"refresh_token":refresh_token})
        serializer.is_valid(raise_exception=True)
        new_access_token = serializer.validated_data["access_token"]
        response_data = APIResponse(
                status_code=status.HTTP_200_OK,
                message="Access token refreshed successfully",
                data={
                    "access_token": new_access_token,
                },
            )

        response = Response(
                data=response_data.to_dict(),
                status=status.HTTP_200_OK,
            )

        response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=new_access_token,
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                max_age=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],  # 24 hours
            )

        return response
