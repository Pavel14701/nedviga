from typing import Optional
from dataclasses import dataclass
from dataclasses import field
from datetime import timedelta

@dataclass(slots=True)
class BaseUser:
    username: str
    firstname:Optional[str] = field(default=None)
    lastname:Optional[str] = field(default=None)
    email:str

@dataclass(slots=True)
class NewUserDTO(BaseUser):
    password:str

@dataclass(slots=True)
class SaveUserDTO(BaseUser):
    uuid: str
    hashed_password: str
    salt: str
    is_active: bool = field(default=True)


@dataclass(slots=True)
class TokenDTO:
    token: str


@dataclass(slots=True)
class AccessRefreshTokenDTO:
    data: dict
    expires_timedelta: Optional[timedelta] = field(default=None)


@dataclass(slots=True)
class HashPasswordDTO:
    password:str
    salt:str


@dataclass(slots=True)
class UserCacheDTO:
    token: str
    username: str
    firstname: Optional[str]
    lastname: Optional[str]
    email: str
    hashed_password: str
    salt: str