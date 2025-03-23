from typing import Protocol, Optional
from abc import abstractmethod


class DeleteUser(Protocol):
    @abstractmethod
    async def delete_user_by_uuid(self, user_uuid: str) -> None: ...


class CheckUserStatus(Protocol):
    @abstractmethod
    async def is_task_cancelled(self, user_uuid: str) -> Optional[bool]: ...


class DBSession(Protocol):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...