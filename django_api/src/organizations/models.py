import uuid

from django.conf import settings
from django.db import models


class Organization(models.Model):

    """
    Representa uma empresa/organização (para planos corpotativos)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organização'
        verbose_name_plural = 'Organizações'

    def __str__(self) -> str:
        return self.name


class OrganizationMember(models.Model):

    """
    Representa a associação entre usuários e organizações
    """

    class RoleChoices(models.TextChoices):
        OWNER = 'OWNER', 'Owner'
        ADMIN = 'ADMIN', 'Admin'
        MEMBER = 'MEMBER', 'Member'

    ROLE_CHOICES = [
        (RoleChoices.OWNER, 'Owner'),
        (RoleChoices.ADMIN, 'Admin'),
        (RoleChoices.MEMBER, 'Member'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=RoleChoices.MEMBER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'organization_members'
        verbose_name = 'Membro da Organização'
        verbose_name_plural = 'Membros da Organização'
        constraints = [
        models.UniqueConstraint(fields=['organization', 'user'], name='unique_org_user')
    ]
        indexes = [
            models.Index(fields=['organization', 'user']),
            models.Index(fields=['user']),
        ]

    def __str__(self) -> str:
        return f"{self.user.email} in {self.organization.name} as {self.role}"
