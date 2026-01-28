import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models

# Create your models here.

class Plan(models.Model):
    """
    Planos de assinatura (individual ou organização).
    """
    class PlanChoices(models.TextChoices):
        FREE = "FREE", "Grátis"
        PRO = "PRO", "Profissional"
        ENTERPRISE = "ENTERPRISE", "Empresarial"

    class UserChoices(models.TextChoices):
        INDIVIDUAL = "INDIVIDUAL", "Individual"
        ORGANIZATION = "ORGANIZATION", "Organização"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    tier = models.CharField(max_length=50, choices=PlanChoices, default=PlanChoices.FREE)
    plan_type = models.CharField(max_length=50, choices=UserChoices, default=UserChoices.INDIVIDUAL)
    max_documents = models.IntegerField(default=10)
    max_storage_mb = models.IntegerField(default=100)
    max_queries = models.IntegerField(default=100)
    max_members = models.IntegerField(null=True, blank=True, help_text="NULL = ilimitado (para planos ORGANIZATION)")
    price_monthly = models.DecimalField( max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'plans'
        verbose_name = 'Plano'
        verbose_name_plural = 'Planos'
        indexes = [
            models.Index(fields=['tier']),
            models.Index(fields=['plan_type']),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.tier} - {self.plan_type})"


class Subscription(models.Model):
    """
    Assinaturas dos planos.
    """

    class StatusChoices(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativo"
        CANCELED = "CANCELED", "Cancelado"
        EXPIRED = "EXPIRED", "Expirado"


    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='subscriptions')
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, null=True, blank=True, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='subscriptions')
    status = models.CharField(max_length=50, choices=StatusChoices, default=StatusChoices.ACTIVE)
    current_period_start = models.DateTimeField(auto_now_add=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subscriptions'
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'
        indexes = [
            models.Index(fields=['user_id', 'status']),
            models.Index(fields=['organization_id', 'status']),
        ]

    def __str__(self) -> str:
        owner: str = self.user.email if self.user else (self.organization.name if self.organization else "Unknown")
        return f"{owner} - {self.plan.name} ({self.status})"


class Usage(models.Model):
    """
    Uso mensal por usuário individual ou organização.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='usage_records',
        help_text='NULL se for uso da org'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='usage_records',
        help_text='NULL se for uso individual'
    )
    period = models.DateField(help_text='mês/ano, ex: 2025-12-01')
    documents_uploaded = models.IntegerField(default=0)
    queries_executed = models.IntegerField(default=0)
    storage_used_mb = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usage'
        verbose_name = 'Uso'
        verbose_name_plural = 'Usos'
        unique_together = [['user', 'period'], ['organization', 'period']]
        indexes = [
            models.Index(fields=['user', 'period']),
            models.Index(fields=['organization', 'period']),
            models.Index(fields=['-period']),
        ]

    def __str__(self) -> str:
        owner: str = self.user.email if self.user else (self.organization.name if self.organization else "Unknown")
        return f"{owner} - {self.period}"
