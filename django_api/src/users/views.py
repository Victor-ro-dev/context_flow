from typing import TYPE_CHECKING

from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.serializers import RegisterSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request


class SignUpView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer: RegisterSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )
