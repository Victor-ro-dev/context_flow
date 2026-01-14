from dataclasses import dataclass


@dataclass(frozen=True) # frozen=True torna o DTO imutável
class UserRegistrationDTO:
    email: str
    username: str
    password: str
    plan_tier: str = "FREE"

@dataclass(frozen=True)
class UserLoginDTO:
    email: str
    password: str
    remember_me: bool = False
