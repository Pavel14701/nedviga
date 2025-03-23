from abc import abstractmethod
from typing import Protocol, Optional
from uuid import UUID

from argon2 import PasswordHasher


from auth.src.domain.entities import (
    DeleteUserTaskDM, 
    GetUserDM, 
    RevokeTokenDM, 
    RevokeTokensDM, 
    UserDM, 
    UserDataDM, 
    SendConfirmEmailDM, 
    UserPasswordDM
)


class Auth(Protocol):

    @abstractmethod
    async def create_access_token(self, params: UserDataDM) -> str: ...

    @abstractmethod
    async def create_refresh_token(self, params: UserDataDM) -> str: ...

    @abstractmethod
    async def verify_access_token(self, token: str) -> Optional[UserDataDM]: ...

    @abstractmethod
    async def verify_refresh_token(self, token: str) -> Optional[UserDataDM]: ...


class Cruds(Protocol):

    @abstractmethod
    async def signup(self, params: UserDM) -> Optional[UserDataDM]: ...

    @abstractmethod
    async def get_user_data(self, params: GetUserDM) -> Optional[UserPasswordDM]: ...


class DeleteUserTask(Protocol):
    @abstractmethod
    async def schedule_user_deletion(self, params: DeleteUserTaskDM) -> None: ...


class SendConfirmationEmail(Protocol):
    @abstractmethod
    async def send_confirmation_email(self, params: SendConfirmEmailDM) -> None: ...


class RedisService(Protocol):
    @abstractmethod
    async def save_user(self, params: UserDM) -> None: ...

    @abstractmethod
    async def load_user(self, user_uuid: str) -> UserDM: ...

    @abstractmethod
    async def delete_user(self, user_uuid: str) -> None: ...

    @abstractmethod
    async def cancel_shedule_user_deletion(self, user_uuid: str) -> None: ...

    @abstractmethod
    async def save_revoked_tokens(self, params: RevokeTokensDM) -> None: ...

    @abstractmethod
    async def is_token_revoked(self, params: RevokeTokenDM) -> bool: ...


class DBSession(Protocol):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...


class UUIDGenerator(Protocol):
    def __call__(self) -> UUID: ...