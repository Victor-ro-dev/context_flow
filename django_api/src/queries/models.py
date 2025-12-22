import uuid

from django.conf import settings
from django.db import models


class QueryLog(models.Model):
    """
    Histórico de consultas RAG (pergunta, resposta, citações, métricas).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='query_logs'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='query_logs',
        help_text='NULL se query pessoal'
    )
    query_text = models.TextField()
    answer_text = models.TextField(blank=True)
    citations = models.JSONField(default=list, blank=True, help_text='Lista de fontes/trechos usados') # type: ignore
    latency_ms = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'query_logs'
        verbose_name = 'Log de Query'
        verbose_name_plural = 'Logs de Queries'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.query_text[:50]}"


class AuditLog(models.Model):
    """
    Log de auditoria de ações importantes do sistema.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        help_text='NULL se ação pessoal'
    )
    action = models.CharField(max_length=100, help_text='LOGIN, CREATE_DOC, DELETE_DOC, QUERY_RAG, etc.')
    resource_type = models.CharField(max_length=100, blank=True)
    resource_id = models.UUIDField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Log de Auditoria'
        verbose_name_plural = 'Logs de Auditoria'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        user_email = self.user.email if self.user else 'Sistema'
        return f"{user_email} - {self.action}"
