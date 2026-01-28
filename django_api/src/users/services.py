from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from users.dtos import UserResponseDTO
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
    from users.models import User

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken, Token


class AuthService:
    """Service para operações de autenticação e registro"""

    @staticmethod
    @transaction.atomic
    def register_user(user_dto: UserRegistrationDTO) -> User:
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
            msg = "Email já em uso"
            raise UserAlreadyExistsException(msg) from None

        # Validação de negócio: username já existe?
        if UserRepository.username_exists(user_dto.username):
            msg = "Username já em uso"
            raise UserAlreadyExistsException(msg) from None

        # Validação de negócio: plano existe?
        plan = PlanRepository.get_by_tier(user_dto.plan)
        if not plan:
            msg = f"Plano '{user_dto.plan}' não existe"
            raise PlanNotFoundException(msg) from None

        # Cria usuário
        user = UserRepository.create(
            email=user_dto.email,
            username=user_dto.username,
            password=user_dto.password,
            plan=user_dto.plan,
            user_type=user_dto.user_type
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
    def authenticate_user(user_dto: UserLoginDTO) -> UserResponseDTO:
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
            msg = "Usuário não encontrado"
            raise UserNotFoundException(msg) from None

        # Valida se usuário está ativo
        if not user.is_active:
            msg = "Usuário inativo"
            raise InvalidCredentialsException(msg) from None

        # Valida senha
        if not user.check_password(user_dto.password):
            msg = "Senha incorreta"
            raise InvalidCredentialsException(msg) from None

        refresh = TokenService.generate_tokens_for_user(user)

        # Atualiza último login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])

        return UserResponseDTO(
            id=str(user.id),
            email=user.email,
            username=user.username,
            plan=user.plan,
            user_type=user.user_type,
            jwt_access=refresh['jwt-access'],
            jwt_refresh=refresh['jwt-refresh']
        )

class TokenService:
    """Service para operações com tokens JWT"""

    @staticmethod
    def generate_tokens_for_user(user: User) -> dict:
        """
        Gera tokens de acesso e refresh para o usuário.

        Args:
            user: Usuário para o qual gerar os tokens
            remember_me: Indica se o token deve ter duração estendida
        Returns:
            dict: Dicionário com 'access' e 'refresh' tokens
        """
        refresh = RefreshToken.for_user(user)
        return {
            'jwt-access': str(refresh.access_token),
            'jwt-refresh': str(refresh),
        }

    @staticmethod
    def validate_refresh_token(refresh_token: Token) -> str:
        """
        Valida o refresh token e retorna o usuário associado.

        Args:
            refresh_token: Token de refresh

        Returns:
            str: Novo token de acesso

        Raises:
            InvalidCredentialsException: Se o token é inválido ou expirado
        """

        try:
            token = RefreshToken(refresh_token)
            new_access_token = str(token.access_token)
        except TokenError as err:
            error_msg = TokenError("Refresh token inválido ou expirado")
            raise InvalidCredentialsException(str(error_msg)) from err

        return new_access_token
