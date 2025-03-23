from dataclasses import dataclass


@dataclass(slots=True)
class SendEmailDM:
    subject: str
    body_html: str
    recipient: str