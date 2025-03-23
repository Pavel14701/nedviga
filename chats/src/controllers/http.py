from typing import Annotated, Literal, Dict, Any

from dishka.integrations.base import FromDishka as Depends
from dishka.integrations.litestar import inject
from litestar import Controller, websocket, WebSocket
from litestar.exceptions import HTTPException
from litestar.params import Body

from chats.src.application.dto import SendMessageDTO
from chats.src.application.interfaces import SendMessage


class ChatController(Controller):
    path = "/chat"

    @websocket(path="/send/{user_type}/{user_id}")
    @inject
    async def send_message_handler(
        self,
        socket: WebSocket,
        token: Annotated[str, Body(description="Токен доступа, используемый для аутентификации и авторизации запросов.")],
        recipient_uuid: Annotated[str, Body(description="Уникальный идентификатор получателя сообщения в чате, используется для указания, кому адресовано сообщение.")],
        chat_uuid: Annotated[str, Body(description="Уникальный идентификатор чата, UUID")],
        content: Annotated[str, Body(description="Текст сообщения, которое нужно отправить")],
        interactor: Depends[SendMessage]
    ) -> None:
        await socket.accept()
        try:
            message_dto = SendMessageDTO(
                token=token, 
                recipient_uuid=recipient_uuid, 
                chat_uuid=chat_uuid
            )
            response = await interactor(message_dto)
            await socket.send_text(f"Сообщение отправлено: {response}")
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")
            await socket.close(code=4001, reason="Ошибка при отправке сообщения.")


    @websocket(path="/edit/{user_type}/{user_id}")
    @inject
    async def edit_message_handler(
        self,
        socket: WebSocket,
        user_type: Annotated[str, Literal["user", "admin"], Body(description="Тип пользователя, например: user или admin")],
        user_id: Annotated[str, Body(description="Уникальный идентификатор пользователя, UUID")],
        message_id: Annotated[str, Body(description="Уникальный идентификатор сообщения, UUID")],
        chat_id: Annotated[str, Body(description="Уникальный идентификатор чата, UUID")],
        new_content: Annotated[str, Body(description="Новый текст сообщения")]
    ) -> None:
        await socket.accept()
        async with SessionLocal() as session:
            try:
                # Редактирование сообщения
                await edit_message(session, message_id, chat_id, new_content)
                await socket.send_text(f"Сообщение {message_id} обновлено.")
            except Exception as e:
                print(f"Ошибка редактирования сообщения: {e}")
                await socket.close(code=4002, reason="Ошибка при редактировании сообщения.")

    @websocket(path="/delete/{user_type}/{user_id}")
    @inject
    async def delete_message_handler(
        self,
        socket: WebSocket,
        user_type: Annotated[str, Literal["user", "admin"], Body(description="Тип пользователя, например: user или admin")],
        user_id: Annotated[str, Body(description="Уникальный идентификатор пользователя, UUID")],
        message_id: Annotated[str, Body(description="Уникальный идентификатор сообщения, UUID")],
        chat_id: Annotated[str, Body(description="Уникальный идентификатор чата, UUID")]
    ) -> None:
        await socket.accept()
        async with SessionLocal() as session:
            try:
                # Удаление сообщения
                await delete_message(session, message_id, chat_id)
                await socket.send_text(f"Сообщение {message_id} удалено.")
            except Exception as e:
                print(f"Ошибка удаления сообщения: {e}")
                await socket.close(code=4003, reason="Ошибка при удалении сообщения.")
