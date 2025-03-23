from dataclasses import dataclass


@dataclass(slots=True)
class SendEmailDTO:
    message_uuid: str
    email: str