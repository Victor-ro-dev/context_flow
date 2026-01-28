from os import access
from typing import TYPE_CHECKING

from rest_framework import serializers

from users.dtos import UserLoginDTO, UserRegistrationDTO, UserResponseDTO
from users.services import AuthService, TokenService

if TYPE_CHECKING:
    from users.models import User


class RegisterSerializer(serializers.Serializer):
    """Serializer para registro de novos usuários"""

    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    plan = serializers.ChoiceField(
        choices=["FREE", "PRO", "PREMIUM"],
        default="FREE",
    )
    user_type = serializers.ChoiceField(
        choices=["INDIVIDUAL", "ORGANIZATION"],
        default="INDIVIDUAL",
        required=False,
    )

    def validate_email(self, value: str) -> str:
        """✅ Validação de formato (é um email válido?)"""
        # EmailField já valida, mas podemos adicionar lógica extra se necessário
        return value

    def validate_username(self, value: str) -> str:
        """✅ Validação de formato (username tem tamanho válido?)"""
        return value

    def create(self, validated_data: dict) -> User:
        """Chama service para criar usuário com validações de negócio"""
        dto = UserRegistrationDTO(**validated_data)
        return AuthService.register_user(dto)



class LoginSerializer(serializers.Serializer):
    """Serializer para autenticação de  usuários"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False, required=False)

    def validate(self, data: dict) -> dict: #type: ignore
        """Validação global: autentica usuário via service"""

        dto = UserLoginDTO(
                email=data['email'],
                password=data['password']
            )

        user_response = AuthService.authenticate_user(dto)
        return {
            "user": user_response}

class RefreshTokenSerializer(serializers.Serializer):
    """Serializer para refresh de token"""
    refresh_token = serializers.CharField(write_only=True)

    def validate(self, data: dict) -> dict: #type: ignore
        """Validação global: valida o refresh token via service"""
        refresh_token = data['refresh_token']
        new_access_token = TokenService.validate_refresh_token(refresh_token)

        return {"access_token": new_access_token}
