from datetime import datetime
from typing import Optional
from dataclasses import field, dataclass, asdict


class BaseDM:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class UserDM(BaseDM):
    uuid: str
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: str
    phone_number: str
    hashed_password: str
    is_active: bool


@dataclass(slots=True)
class UserPasswordDM(BaseDM):
    hashed_password: str
    uuid: str
    username: str
    is_active: bool
    role: str


@dataclass(slots=True)
class UserDataDM(BaseDM):
    uuid: str
    username: str
    is_active: bool = field(default=False)
    role: str = field(default="user")
    exp: Optional[datetime] = None


@dataclass(slots=True)
class TokenDM(BaseDM):
    access_token: str
    refresh_token: str
    bearer: str = field(default="Bearer")


@dataclass(slots=True)
class RevokeTokensDM:
    access_token: str
    access_exp: float
    refresh_token: str
    refresh_exp: float


@dataclass(slots=True)
class DeleteUserTaskDM(BaseDM):
    user_uuid: str
    delay: int


@dataclass(slots=True)
class SendConfirmEmailDM(BaseDM):
    uuid: str
    email: str
    username: str


@dataclass(slots=True)
class GetUserDM:
    phone: Optional[str]
    username: Optional[str]


@dataclass(slots=True)
class RevokeTokenDM:
    token: str
    token_type: str