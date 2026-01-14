from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from users.exceptions import (
    InvalidCredentialsException,
    PlanNotFoundException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from users.repositories import (
    PlanRepository,
    SubscriptionRepository,
    UsageRepository,
    UserRepository,
)

if TYPE_CHECKING:
    from users.dtos import UserLoginDTO, UserRegistrationDTO


class AuthService:
    """Service para operações de autenticação e registro"""

    @staticmethod
    @transaction.atomic
    def register_user(user_dto: UserRegistrationDTO):
        """
        Registra novo usuário e cria subscription.

        Args:
            user_dto: Data Transfer Object com dados do usuário

        Returns:
            User: Usuário criado

        Raises:
            UserAlreadyExistsException: Se email ou username já existem
            PlanNotFoundException: Se plano não existe
        """
        # Validação de negócio: email já existe?
        if UserRepository.email_exists(user_dto.email):
            raise UserAlreadyExistsException("Email já em uso")

        # Validação de negócio: username já existe?
        if UserRepository.username_exists(user_dto.username):
            raise UserAlreadyExistsException("Username já em uso")

        # Validação de negócio: plano existe?
        plan = PlanRepository.get_by_tier(user_dto.plan_tier)
        if not plan:
            raise PlanNotFoundException(f"Plano '{user_dto.plan_tier}' não existe")

        # Cria usuário
        user = UserRepository.create(
            email=user_dto.email,
            username=user_dto.username,
            password=user_dto.password,
            role=user_dto.plan_tier
        )

        # Cria subscription
        now = timezone.now()
        SubscriptionRepository.create(
            user=user,
            plan=plan,
            status='ACTIVE',
            current_period_start=now,
            current_period_end=now + timedelta(days=30)
        )

        # Cria usage inicial
        period = now.strftime("%Y-%m-%d")
        UsageRepository.get_or_create_period_usage(
            user=user,
            period=period
        )

        return user

    @staticmethod
    def authenticate_user(user_dto: UserLoginDTO):
        """
        Autentica usuário por email e senha.

        Args:
            user_dto: Data Transfer Object com email e senha

        Returns:
            User: Usuário autenticado

        Raises:
            UserNotFoundException: Se usuário não existe
            InvalidCredentialsException: Se senha está errada ou usuário inativo
        """
        # Busca usuário
        user = UserRepository.get_by_email(user_dto.email)
        if not user:
            raise UserNotFoundException("Usuário não encontrado")

        # Valida se usuário está ativo
        if not user.is_active:
            raise InvalidCredentialsException("Usuário inativo")

        # Valida senha
        if not user.check_password(user_dto.password):
            raise InvalidCredentialsException("Senha incorreta")

        # Atualiza último login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return user
