from typing import TYPE_CHECKING

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.response_handler import APIResponse
from users.serializers import LoginSerializer, RegisterSerializer

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
        serializer: RegisterSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response = APIResponse(
            status_code=status.HTTP_201_CREATED,
            message="User registered successfully",
            data={
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "role": user.role,
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
        "password": "password123"
    }
    """

    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        """Autentica usuário"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        response = APIResponse(
            status_code=status.HTTP_200_OK,
            message="Login successful",
            data={
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
            },
            error=None,
            trace_id=None,
            timestamp=None,
        )

        return Response(
            data=response.to_dict(),
            status=status.HTTP_200_OK,
        )
