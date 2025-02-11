from abc import abstractmethod
from typing import Protocol, Optional, Any
from uuid import UUID

from sqlalchemy import Row
from litestar.security.jwt.auth import (
    OAuth2Login,
    OAuth2PasswordBearerAuth,
)

from src.domain import entities


class UUIDGenerator(Protocol):
    def __call__(self) -> UUID:
        ...


class SaltGeneratorInterface(Protocol):
    @abstractmethod
    async def generate_salt(self) -> str:
        ...


class PasswordHasherInterface(Protocol):
    @abstractmethod
    async def hash_password_with_salt(self, data: entities.HashPasswordMethodDM) -> str:
        ...


class SignupInterface(Protocol):
    @abstractmethod
    async def signup(self, data: entities.TokenDM) -> dict[str, str]:
        ...


class CreateAccessTokenInterface(Protocol):
    @abstractmethod
    async def create_access_token(self, data: entities.AccessRefreshTokenDM) -> str:
        ...


class CreateRefreshTokenInterface(Protocol):
    @abstractmethod
    async def create_refresh_token(self, data: entities.AccessRefreshTokenDM) -> str:
        ...


class VerifyTokenInterface(Protocol):
    @abstractmethod
    async def verify_token(self, token: entities.TokenDM) -> Optional[str]:
        ...


class CreateNewUserInterface(Protocol):
    @abstractmethod
    async def create_new_user(self, user: entities.NewUserDM) -> Optional[Row[Any]]:
        ...



class GetUserDataInterface(Protocol):
    @abstractmethod
    async def get_user_data(self, form_data: OAuth2Login) -> entities.UserDataDM:
        ...


class GetOAuthSchemeInterface(Protocol):
    @abstractmethod
    async def get_oauth_scheme(self, path: str) -> OAuth2PasswordBearerAuth:
        ...

class DBSession(Protocol):
    @abstractmethod
    async def commit(self) -> None:
        ...

    @abstractmethod
    async def flush(self) -> None:
        ...