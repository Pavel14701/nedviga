from events.src.application.interfaces import CheckUserStatus, DeleteUser, DBSession

class DeleteUserInteractor:
    def __init__(
        self,
        status_gateway: CheckUserStatus,
        delete_gateway: DeleteUser,
        session: DBSession,
    ) -> None:
        self._status_gateway = status_gateway
        self._delete_gateway = delete_gateway
        self._session = session

    async def __call__(self, user_uuid: str) -> None:
        status = await self._status_gateway.is_task_cancelled(user_uuid=user_uuid)
        if not status:
            await self._delete_gateway.delete_user_by_uuid(user_uuid=user_uuid)
            await self._session.commit()