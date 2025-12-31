from rest_framework import serializers  # type: ignore

from users.models import User

from .dtos import UserRegistrationDTO
from .services import register_user


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    plan_tier = serializers.ChoiceField(
        choices=["FREE", "PRO", "PREMIUM"],
        default="FREE",
    )

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email já está em uso.")
        return value

    def create(self, validated_data: dict) -> User:
        dto = UserRegistrationDTO(**validated_data
        )
        return register_user(dto)
