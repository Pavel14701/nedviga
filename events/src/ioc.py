from typing import AsyncIterable

from dishka import Provider, Scope, provide, AnyOf, from_context
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from events.src.application import interfaces
from events.src.application.interactors import DeleteUserInteractor
from events.src.config import Config
from events.src.infrastructure.database import new_session_maker
from events.src.infrastructure.gateways import CrudsGateway


class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(self, session_maker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AnyOf[
        AsyncSession,
        interfaces.DBSession,
    ]]:
        async with session_maker() as session:
            yield session

    cruds_gateway = provide(
        CrudsGateway,
        scope=Scope.REQUEST,
        provides=interfaces.DeleteUser
    )

    delete_user_interactor = provide(DeleteUserInteractor, scope=Scope.REQUEST)