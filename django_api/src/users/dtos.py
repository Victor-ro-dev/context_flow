from dataclasses import dataclass
from os import access
from venv import create


@dataclass(frozen=True)
class UserRegistrationDTO:
    """DTO para registro de novo usuário"""
    email: str
    username: str
    password: str
    plan: str = "FREE"
    user_type: str = "INDIVIDUAL"

@dataclass(frozen=True)
class UserLoginDTO:
    """DTO para autenticação de usuário"""
    email: str
    password: str
    remember_me: bool = False

@dataclass(frozen=True)
class UserResponseDTO:
    """DTO de resposta com dados de usuário autenticado"""
    id: str
    email: str
    username: str
    plan: str
    user_type: str | None = None
    jwt_access: str = ""
    jwt_refresh: str = ""
    created_at: str | None = None
