from dishka.integrations.base import FromDishka as Depends
from faststream.rabbit import RabbitRouter

from events.src.application.interactors import DeleteUserInteractor


TasksController=RabbitRouter()


@TasksController.subscriber("delete_rotten_user")
async def delete_user(
    message: dict,
    interactor: Depends[DeleteUserInteractor]
) -> None:
    user_uuid = message.get("user_uuid")
    await interactor(user_uuid)
