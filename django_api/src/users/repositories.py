from typing import Optional

from plans.models import Plan, Subscription, Usage
from users.models import User


class UserRepository:
    """Repository para operações de User"""

    @staticmethod
    def get_by_email(email: str) -> User | None:
        """Busca usuário por email"""
        return User.objects.filter(email=email).first()

    @staticmethod
    def get_by_username(username: str) -> User | None:
        """Busca usuário por username"""
        return User.objects.filter(username=username).first()

    @staticmethod
    def email_exists(email: str) -> bool:
        """Verifica se email já existe"""
        return User.objects.filter(email=email).exists()

    @staticmethod
    def username_exists(username: str) -> bool:
        """Verifica se username já existe"""
        return User.objects.filter(username=username).exists()

    @staticmethod
    def create(
        email: str,
        username: str,
        password: str,
        plan: str = User.PlanChoices.FREE,
        user_type: str = User.UserTypeChoices.INDIVIDUAL
    ) -> User:
        """Cria novo usuário"""
        return User.objects.create_user(
            email=email,
            username=username,
            password=password,
            plan=plan,
            user_type=user_type
        )

    @staticmethod
    def get_active_users() -> list[User]:
        """Retorna todos os usuários ativos"""
        return list(User.objects.filter(is_active=True))


class PlanRepository:
    """Repository para operações de Plan"""

    @staticmethod
    def get_by_tier(tier: str) -> Plan | None:
        """Busca plano por tier (FREE, PRO, PREMIUM)"""
        return Plan.objects.filter(
            tier=tier,
            plan_type=Plan.UserChoices.INDIVIDUAL
        ).first()


class SubscriptionRepository:
    """Repository para operações de Subscription"""

    @staticmethod
    def create(
        user: User,
        plan: Plan,
        status: str = Subscription.StatusChoices.ACTIVE,
        current_period_start=None,
        current_period_end=None
    ) -> Subscription:
        """Cria nova subscription"""
        return Subscription.objects.create(
            user=user,
            plan=plan,
            status=status,
            organization=None,
            current_period_start=current_period_start,
            current_period_end=current_period_end
        )


class UsageRepository:
    """Repository para operações de Usage"""

    @staticmethod
    def get_or_create_period_usage(
        user: User,
        period: str,
        defaults: dict | None = None
    ) -> Usage:
        """Pega ou cria usage para um período"""
        if defaults is None:
            defaults = {
                "documents_uploaded": 0,
                "queries_executed": 0,
                "storage_used_mb": 0,
                "tokens_used": 0,
            }

        usage, _ = Usage.objects.get_or_create(
            user=user,
            organization=None,
            period=period,
            defaults=defaults
        )
        return usage
