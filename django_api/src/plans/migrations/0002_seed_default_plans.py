from decimal import Decimal

from django.db import migrations


def create_default_plans(apps, schema_editor):
    Plan = apps.get_model("plans", "Plan")

    plans_data = [
        {
            "name": "Free",
            "tier": "FREE",
            "plan_type": "INDIVIDUAL",
            "price_monthly": Decimal("0.00"),
            "max_documents": 10,
            "max_storage_mb": 100,
            "max_queries": 100,
            "max_members": 1,
            "description": "Plano gratuito básico para testes.",
        },
        {
            "name": "Pro",
            "tier": "PRO",
            "plan_type": "INDIVIDUAL",
            "price_monthly": Decimal("19.90"),
            "max_documents": 100,
            "max_storage_mb": 5_000,
            "max_queries": 5_000,
            "max_members": 1,
            "description": "Plano profissional para uso intenso individual.",
        },
        {
            "name": "Premium",
            "tier": "PREMIUM",
            "plan_type": "INDIVIDUAL",
            "price_monthly": Decimal("49.90"),
            "max_documents": -1,        # -1 = ilimitado (se você usou essa convenção)
            "max_storage_mb": 50_000,
            "max_queries": -1,
            "max_members": 1,
            "description": "Plano premium com limites praticamente ilimitados.",
        },
    ]

    for data in plans_data:
        # idempotente: se rodar de novo, atualiza em vez de duplicar
        Plan.objects.update_or_create(
            tier=data["tier"],
            plan_type=data["plan_type"],
            defaults=data,
        )


def remove_default_plans(apps, schema_editor):
    Plan = apps.get_model("plans", "Plan")
    Plan.objects.filter(
        tier__in=["FREE", "PRO", "PREMIUM"],
        plan_type="INDIVIDUAL",
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("plans", "0001_initial"),  # ajuste para o nome da sua primeira migration
    ]

    operations = [
        migrations.RunPython(create_default_plans, remove_default_plans),
    ]