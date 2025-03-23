from dishka.integrations.base import FromDishka as Depends
from dishka.integrations.base import wrap_injection
from faststream.rabbit import RabbitRouter

from mail.src.application.dto import SendEmailDTO
from mail.src.application.interactors import SendSignupMailInteractor


EmailController=RabbitRouter()


class EmailHandler:
    @EmailController.subscriber("send_register_confirmation")
    @wrap_injection
    async def registration_handler(
        message: dict,
        interactor: Depends[SendSignupMailInteractor]
    ) -> str:
        params = SendEmailDTO(
            message_uuid=message.get("message_uuid"),
            email=message.get("email")
        )
        await interactor(params)