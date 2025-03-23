from typing import Optional
from dataclasses import dataclass


@dataclass(slots=True)
class SignupDTO:
    firstname: str
    lastname: str
    username: str
    email: str
    phone: Optional[str] = None
    password: str


@dataclass(slots=True)
class LoginDTO:
    username: Optional[str] = None
    phone: Optional[str] = None
    password: str


@dataclass(slots=True)
class TokensDTO:
    access_token: str
    refresh_token: str