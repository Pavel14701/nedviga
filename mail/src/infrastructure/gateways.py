from logging import Logger
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib

from mail.src.application.interfaces import EmailSender
from mail.src.config import EmailConfig
from mail.src.domain.entities import SendEmailDM


class SendEmailGateway(EmailSender):
    def __init__(
        self, 
        config: EmailConfig,
        logger: Logger
    ) -> None:
        self._config = config
        self._logger = logger

    async def send_html_email(self, params: SendEmailDM) -> None:
        message = MIMEMultipart("alternative")
        message["Subject"] = params.subject
        message["From"] = self._config.sender_email
        message["To"] = params.recipient
        message.attach(MIMEText(params.body_html, "html"))
        try:
            await aiosmtplib.send(
                message,
                hostname=self._config.smtp_host,
                port=self._config.smtp_port
            )
            self._logger.info(f"Email successfully sent to {params.recipient}")
        except Exception as e:
            self._logger.error(f"Failed to send email to {params.recipient}: {e}")