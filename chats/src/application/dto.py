from dataclasses import dataclass
from re import S


@dataclass(slots=True)
class SendMessageDTO:
    token: str
    recipient_uuid: str
    chat_uuid: str
    content: str