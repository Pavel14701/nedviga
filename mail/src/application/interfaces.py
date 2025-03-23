from abc import abstractmethod
from typing import Protocol

from mail.src.domain.entities import SendEmailDM


class GetTemplates(Protocol):
    @abstractmethod 
    def registration_template(self, uuid: str) -> str: ...


class EmailSender(Protocol):
    @abstractmethod
    async def send_html_email(self, params: SendEmailDM) -> None: ...