from typing import AsyncIterable
from contextlib import asynccontextmanager
from uuid import uuid4

from dishka import Provider, Scope, provide, AnyOf, from_context
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from faststream.rabbit import RabbitBroker
from redis.asyncio import Redis, ConnectionPool
from argon2 import PasswordHasher

from auth.src.application import interfaces
from auth.src.application.interactors import (
    SignupInteractor,
    ConfirmSignupInteractor,
    LoginInteractor,
    RefreshTokenInteractor,
    VerifyTokenInteractor,
    LogoutInteractor
)
from auth.src.config import AppConfig, Config, SecurityConfig
from auth.src.infrastructure.broker import new_broker
from auth.src.infrastructure.cache import new_redis_client
from auth.src.infrastructure.database import new_session_maker
from auth.src.infrastructure.gateways import (
    CacheGateway, 
    CrudsGateway, 
    AuthGateway, 
    TasksGateway
)

class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_security_config(self, config: Config) -> SecurityConfig:
        return config.security

    @provide(scope=Scope.APP)
    def get_app_config(self, config: Config) -> AppConfig:
        return config.app

    hasher = from_context(provides=PasswordHasher, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_uuid_generator(self) -> interfaces.UUIDGenerator:
        return uuid4

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, 
        session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AnyOf[
        AsyncSession,
        interfaces.DBSession,
    ]]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.APP)
    def get_cache_connection_pool(self, config: Config) -> ConnectionPool: 
        return new_redis_client(config.redis)

    @provide(scope=Scope.REQUEST)
    async def get_redis_conn(self, conn_pool: ConnectionPool) -> AsyncIterable[Redis]:
        async with asynccontextmanager(lambda: Redis(connection_pool=conn_pool))() as conn:
            yield conn

    @provide(scope=Scope.APP)
    def get_broker(self, config: Config) -> RabbitBroker:
        return new_broker(config.rabbitmq)

    auth_gateway = provide(
        AuthGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[interfaces.Auth]
    )

    cruds_gateway = provide(
        CrudsGateway,
        scope=Scope.REQUEST,
        provides=interfaces.Cruds
    )

    cache_gateway = provide(
        CacheGateway,
        scope=Scope.REQUEST,
        provides=interfaces.RedisService
    )

    tasks_gateway = provide(
        TasksGateway,
        scope=Scope.REQUEST,
        provides=AnyOf[interfaces.DeleteUserTask, interfaces.SendConfirmationEmail]
    )

    signup_interactor = provide(SignupInteractor, scope=Scope.REQUEST)
    login_interactor = provide(LoginInteractor, scope=Scope.REQUEST)
    confirm_login_interactor = provide(ConfirmSignupInteractor, scope=Scope.REQUEST)
    refresh_interactor = provide(RefreshTokenInteractor, scope=Scope.REQUEST)
    verify_interactor = provide(VerifyTokenInteractor, scope=Scope.REQUEST)
    logout_interactor = provide(LogoutInteractor, scope=Scope.REQUEST)