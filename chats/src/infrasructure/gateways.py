from datetime import datetime, timezone
from typing import List
import uuid

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from chats.src.config import AuthConfig
from chats.src.application.interfaces import (
    GetMessages, SendMessage,
    DeleteMessage, EditMessage,
    AuthService
)
from chats.src.domain.entities import (
    DeleteMessageDM, EditMessageDM, GetMessagesDM, 
    MessageDM, SendMessageDM
)


class Gateways(
    GetMessages, SendMessage, DeleteMessage, 
    EditMessage, AuthService
):

    def __init__(
        self,
        auth_config: AuthConfig,
        session: AsyncSession,
    ) -> None:
        self._auth_config = auth_config
        self._session = session

    async def verify_token_with_auth_service(self, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=self._auth_config.url,
                json={"token": token}
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise ValueError("Токен недействителен или истёк.")


    async def handle_message(self, params: SendMessageDM) -> None:
        message_uuid = str(uuid.uuid4())
        sql = text("""
            INSERT INTO messages (
                uuid, chat_uuid, sender_type, sender_uuid, 
                recipient_type, recipient_uuid, 
                message
            ) VALUES (
                :uuid, :chat_uuid, :sender_type, :sender_uuid, 
                :recipient_type, :recipient_uuid, 
                :message
            )
        """)
        await self._session.execute(sql, {
            "uuid": message_uuid,
            "chat_uuid": params.chat_uuid,
            "sender_type": params.user_type,
            "sender_uuid": params.user_uuid,
            "recipient_type": params.recipient_type,
            "recipient_uuid": params.recipient_uuid,
            "message": params.message
        })


    async def get_chat_messages(self, params: GetMessagesDM) -> List[MessageDM]:
        query = text("""
            SELECT * 
            FROM messages
            WHERE chat_uuid = :chat_uuid
            ORDER BY timestamp DESC
            LIMIT :limit OFFSET :offset
        """)
        result = await self._session.execute(
            statement=query, 
            params={
                "chat_uuid": params.chat_uuid,
                "limit": params.limit,
                "offset": params.offset
        })
        return [MessageDM(**row) for row in result.mappings()]

    async def edit_message(self, params: EditMessageDM) -> MessageDM:
        query = text("""
            UPDATE messages
            SET 
                message = :new_content,
                is_edited = TRUE,
                edited_at = :edited_at
            WHERE 
                uuid = :message_id AND chat_uuid = :chat_id AND sender_uuid = :user_id
        """)
        result = await self._session.execute(query, {
            "new_content": params.new_content,
            "edited_at": datetime.now(timezone.utc),
            "message_id": params.message_uuid,
            "chat_id": params.chat_uuid,
            "user_id": params.user_uuid
        })
        if row := result.mappings().first():
            return MessageDM(**row)
        else:
            raise PermissionError("Вы можете редактировать только свои сообщения.")

    async def delete_message(self, params: DeleteMessageDM) -> None:
        query = text("""
            DELETE FROM messages
            WHERE uuid = :message_id AND chat_uuid = :chat_id AND sender_uuid = :user_id
        """)
        result = await self._session.execute(query, {
            "message_id": params.message_uuid,
            "chat_id": params.chat_uuid,
            "user_id": params.user_uuid
        })
        if result.fetchone():
            await self._session.commit()
        else:
            raise PermissionError("Вы можете удалять только свои сообщения.")