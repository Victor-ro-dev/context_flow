from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import transaction
from django.utils import timezone

from plans.models import Plan, Subscription, Usage
from users.models import User

if TYPE_CHECKING:
    from dtos import UserRegistrationDTO


@transaction.atomic
def register_user(user_dto: UserRegistrationDTO) -> User:
    """
    Registers a new user and creates a subscription based on the selected plan tier.

    Args:
        email (str): The email of the user.
        username (str): The username of the user.
        password (str): The password for the user.
        plan_tier (str): The tier of the plan to subscribe to. Defaults to "FREE".

    Returns:
        User: The created User instance.
    """
    # Create the user
    user = User.objects.create_user(
        email=user_dto.email,
        username=user_dto.username,
        password=user_dto.password,
        role=user_dto.plan_tier
    )

    # Retrieve the selected plan
    try:
        plan = Plan.objects.get(tier=user_dto.plan_tier, plan_type=Plan.PlanChoices.INDIVIDUAL)
    except Plan.DoesNotExist:
        raise ValueError(f"Plano '{user_dto.plan_tier}' não existe.")

    now = timezone.now()

    # Create a subscription for the user
    Subscription.objects.create(
        user=user,
        plan=plan,
        status='ACTIVE',
        organization=None,
        current_period_start=now,
        current_period_end=now + timedelta(days=30)
    )

    period = now.strftime("%Y-%m-%d")  # Ex: "2025-12-31"
    Usage.objects.get_or_create(
        user=user,
        organization=None,
        period=period,
        defaults={
            "documents_uploaded": 0,
            "queries_executed": 0,
            "storage_used_mb": 0,
            "tokens_used": 0,
        },
    )

    return user
