from typing import Optional

from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from events.src.application.interfaces import DeleteUser


class CrudsGateway(DeleteUser):
    def __init__(
        self, 
        session: AsyncSession,
        redis_client: Redis
    ) -> None:
        self._session = session
        self._redis_client = redis_client

    async def delete_user_by_uuid(self, user_uuid: str) -> None:
        user_exists_query = "SELECT uuid FROM users WHERE uuid = :uuid"
        user_exists: Result = await self._session.execute(
            statement=user_exists_query,
            params={"uuid": user_uuid}
        )
        user = user_exists.fetchone()
        if not user:
            return
        delete_query = "DELETE FROM users WHERE uuid = :uuid"
        await self._session.execute(delete_query, {"uuid": user_uuid})

    async def is_task_cancelled(self, user_uuid: str) -> bool:
        cancelled = await self._redis_client.get(f"task:{user_uuid}:cancelled")
        return cancelled is not None