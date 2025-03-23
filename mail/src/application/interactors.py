from mail.src.application.dto import SendEmailDTO
from mail.src.application.interfaces import EmailSender, GetTemplates
from mail.src.domain.entities import SendEmailDM

class SendSignupMailInteractor:
    def __init__(
        self,
        templates_gateway: GetTemplates,
        send_email_gateway: EmailSender
    ) -> None:
        self._templates_gateway = templates_gateway
        self._send_email_gateway = send_email_gateway

    async def __call__(self, params: SendEmailDTO) -> None:
        body_html = self._templates_gateway.registration_template(params.message_uuid)
        params = SendEmailDM(
            subject="Подтверждение регистрации аккаунта",
            body_html=body_html,
            recipient=params.email
        )
        await self._send_email_gateway.send_html_email(params)