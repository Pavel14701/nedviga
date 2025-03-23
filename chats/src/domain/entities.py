from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


class BaseDM:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class SendMessageDM(BaseDM):
    chat_uuid: str
    user_type: str
    user_uuid: str
    recipient_type: str
    recipient_uuid: str
    message: str


@dataclass(slots=True)
class EditMessageDM(BaseDM):
    user_uuid: str
    message_uuid: str
    chat_uuid: str
    new_content: str


@dataclass(slots=True)
class DeleteMessageDM(BaseDM):
    user_uuid: str
    message_uuid: str
    chat_uuid: str


@dataclass(slots=True)
class GetMessagesDM(BaseDM):
    chat_uuid: str
    limit: int
    offset: int


@dataclass(slots=True)
class MessageDM:
    uuid: str
    chat_uuid: str
    sender_type: str
    sender_uuid: str
    recipient_type: str
    recipient_uuid: str
    message: str
    timestamp: datetime
    is_edited: bool
    edited_at: Optional[datetime]
