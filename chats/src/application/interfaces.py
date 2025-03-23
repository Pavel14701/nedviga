from typing import List, Protocol
from abc import abstractmethod
from uuid import UUID

from chats.src.domain.entities import (
    DeleteMessageDM, EditMessageDM, GetMessagesDM, 
    MessageDM, SendMessageDM
)


class AuthService(Protocol):
    @abstractmethod
    async def verify_token_with_auth_service(self, token: str) -> dict: ...


class SendMessage(Protocol):
    @abstractmethod
    async def handle_message(self, params: SendMessageDM) -> None: ...


class GetMessages(Protocol):
    @abstractmethod
    async def get_chat_messages(self, params: GetMessagesDM) -> List[MessageDM]: ...


class EditMessage(Protocol):
    @abstractmethod
    async def edit_message(self, params: EditMessageDM) -> MessageDM: ...


class DeleteMessage(Protocol):
    @abstractmethod
    async def delete_message(self, params: DeleteMessageDM) -> None: ...


class UUIDGenerator(Protocol):
    def __call__(self) -> UUID: ...


class DBSession(Protocol):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...