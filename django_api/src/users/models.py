import uuid
from typing import Any

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.db import models


class UserManager(BaseUserManager["User"]):
    def create_user(
        self,
        email: str,
        username: str,
        password: str | None = None,
        **extra_fields: Any
    ) -> User:
        if not email:
            raise ValueError('O email é obrigatório')
        if not username:
            raise ValueError('O username é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        username: str,
        password: str | None = None,
        **extra_fields: Any
    ) -> User:
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('FREE', 'Free'),
        ('PRO', 'Pro'),
        ('PREMIUM', 'Premium'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._-]+$',
                message='Username pode conter apenas letras, números, pontos, hífens e underscores.',
                code='invalid_username'
            )
        ]
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='FREE')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects: UserManager = UserManager() # type: ignore[assignment]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'users'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self) -> str:
        return self.email
