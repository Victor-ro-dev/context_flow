from rest_framework import serializers

from users.dtos import UserLoginDTO, UserRegistrationDTO
from users.exceptions import (
    InvalidCredentialsException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from users.models import User
from users.services import AuthService


class RegisterSerializer(serializers.Serializer):
    """Serializer para registro de novos usuários"""

    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    plan_tier = serializers.ChoiceField(
        choices=["FREE", "PRO", "PREMIUM"],
        default="FREE",
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
        try:
            dto = UserRegistrationDTO(**validated_data)
            return AuthService.register_user(dto)
        except UserAlreadyExistsException:
            raise


class LoginSerializer(serializers.Serializer):
    """Serializer para autenticação de usuários"""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False, required=False)

    def validate(self, data: dict) -> dict: #type: ignore
        """Validação global: autentica usuário via service"""
        try:
            dto = UserLoginDTO(
                email=data['email'],
                password=data['password']
            )
            user = AuthService.authenticate_user(dto)
            data['user'] = user
        except UserNotFoundException:
            raise
        except InvalidCredentialsException:
            raise

        return data
