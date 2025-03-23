from dishka.integrations.base import FromDishka as Depends
from faststream.rabbit import RabbitRouter

from auth.src.application.interactors import VerifyTokenInteractor
from auth.src.controllers.schemas import UserAuthResponse


AuthMQController = RabbitRouter()


@AuthMQController.subscriber("get_auth_data")
@AuthMQController.publisher("return_auth_data")
async def verify_token(
    token: str,
    interactor: Depends[VerifyTokenInteractor]
) -> UserAuthResponse:
    user_dm = await interactor(token)
    if not user_dm:
        return {"status": "error", "message": "Invalid token or user not activated"}
    return UserAuthResponse(**user_dm)