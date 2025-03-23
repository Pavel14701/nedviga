from typing import Optional
from dataclasses import dataclass, field


@dataclass(slots=True)
class SignupDTO:
    firstname: str
    lastname: str
    username: str
    email: str
    password: str
    phone: Optional[str] = field(default=None)


@dataclass(slots=True)
class LoginDTO:
    password: str
    username: Optional[str] = field(default=None)
    phone: Optional[str] = field(default=None)


@dataclass(slots=True)
class TokensDTO:
    access_token: str
    refresh_token: str