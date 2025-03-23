import json
from datetime import timedelta, datetime, timezone
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from faststream.rabbit import RabbitBroker
from faststream.rabbit.message import RabbitMessage
from redis.asyncio import Redis
from sqlalchemy import text

from auth.src.application.interfaces import (
    Cruds,
    DeleteUserTask, 
    Auth, 
    RedisService, 
    SendConfirmationEmail
)
from auth.src.config import SecurityConfig
from auth.src.domain.entities import (
    GetUserDM,
    RevokeTokenDM,
    RevokeTokensDM, 
    UserDM, 
    SendConfirmEmailDM, 
    UserDataDM, 
    UserPasswordDM
)


class AuthGateway(Auth):
    def __init__(self,config: SecurityConfig) -> None:
        self._config = config

    async def _create_token(self, params: UserDataDM, expire_delta: timedelta, key: str) -> str:
        to_encode: Dict[str, Any] = {
            "uuid": params.uuid,
            "role": params.role,
            "is_active": params.is_active,
            "exp": (datetime.now(timezone.utc) + expire_delta).timestamp()
        }
        return jwt.encode(to_encode, key, algorithm=self._config.algorithm)

    async def create_access_token(self, params: UserDataDM) -> str:
        return await self._create_token(
            params=params,
            expire_delta=timedelta(minutes=self._config.access_token_expire_minutes),
            key=self._config.secret_access_key
        )

    async def create_refresh_token(self, params: UserDataDM) -> str:
        return await self._create_token(
            params=params,
            expire_delta=timedelta(days=self._config.refresh_access_token_expire_days),
            key=self._config.secret_refresh_key
        )

    async def _verify_token(self, token: str, key: str) -> Optional[dict]:
        try:
            payload = jwt.decode(
                token=token,
                key=key,
                algorithms=[self._config.algorithm]
            )
            return payload
        except JWTError:
            return None

    async def verify_access_token(self, token: str) -> Optional[UserDataDM]:
        payload = await self._verify_token(token, self._config.secret_access_key)
        return UserDataDM(**payload) or None

    async def verify_refresh_token(self, token: str) -> Optional[UserDataDM]:
        payload = await self._verify_token(token, self._config.secret_refresh_key)
        return UserDataDM(**payload) or None


class CrudsGateway(Cruds):
    def __init__(
        self,
        redis_client: Redis,
        db_session: AsyncSession,
        config: SecurityConfig
    ) -> None:
        self._db_session = db_session
        self._redis_client = redis_client
        self._config = config

    async def signup(self, params: UserDM) -> Optional[UserDataDM]:
        query = text("""
            INSERT INTO users (
                uuid, email, username, 
                firstname, lastname, phone_number, 
                hashed_password, is_active
            )
            VALUES (
                :uuid, :email, :username, 
                :firstname, :lastname, :phone_number, 
                :hashed_password, :is_active
            )
            RETURNING uuid, username, is_active, role;
        """)
        result = await self._db_session.execute(
            statement=query,
            params=params.to_dict()
        )
        if row := result.fetchone():
            return UserDataDM(**row._mapping)
        return

    async def get_user_data(self, params: GetUserDM) -> Optional[UserPasswordDM]:
        if params.username:
            query = text("""
                SELECT (
                    hashed_password, 
                    uuid, username, is_active, role 
                FROM users 
                WHERE username = :username
            """)
            query_params = {"username": params.username}
        if params.phone:
            query = text("""
                SELECT (
                    hashed_password, 
                    uuid, username, is_active, role 
                FROM users 
                WHERE phone_number = :phone
            """)
            query_params = {"phone": params.phone}
        else:
            return
        result = await self._db_session.execute(
            statement=query,
            params=query_params
        )
        if row := result.fetchone():
            return UserPasswordDM(**row._mapping)
        return


class CacheGateway(RedisService):
    def __init__(self, redis_client: Redis) -> None:
        self._redis_client = redis_client

    async def save_user(self, params: UserDataDM) -> None:
        user_data = json.dumps(params.to_dict())
        await self._redis_client.setex(
            name=f'user_{params.uuid}',
            time=1800,
            value=user_data
        )

    async def load_user(self, user_uuid: str) -> UserDataDM:
        user_json = self._redis_client.get(name=f'user_{user_uuid}')
        return UserDataDM(**json.loads(user_json))

    async def delete_user(self, user_uuid: str) -> None:
        await self._redis_client.delete(f'user_{user_uuid}')

    async def cancel_shedule_user_deletion(self, user_uuid: str) -> None:
        await self._redis_client.set(f"task:{user_uuid}:cancelled", "true", ex=1800)

    async def _save_revoked_token(
        self, 
        token: str, 
        exp: float, 
        now: float,
        token_type: str
    ) -> None:
        ttl = max(0, int(exp - now))
        await self._redis_client.set(
            key=f"revoked:{token_type}:{token}",
            value="revoked",
            ex=ttl
        )

    async def save_revoked_tokens(self, params: RevokeTokensDM) -> bool:
        now = datetime.now(timezone.utc).timestamp()
        tokens = [params.access_token, params.refresh_token]
        exps = [params.access_exp, params.refresh_exp]
        token_types = ["access", "refresh"]
        async for token, exp, token_type in zip(tokens, exps, token_types):
            await self._save_revoked_token(token, exp, now, token_type)
        return True

    async def is_token_revoked(self, params: RevokeTokenDM) -> bool:
        revoked = await self._redis_client.get(
            f"revoked:{params.token_type}:{params.token}"
        )
        return revoked is not None


class TasksGateway(DeleteUserTask, SendConfirmationEmail):
    def __init__(
        self, 
        rabbitmq_broker: RabbitBroker,
    ) -> None:
        self._broker = rabbitmq_broker

    async def schedule_user_deletion(self, user_uuid: str) -> None:
        async with self._broker as broker:
            await broker.publish(
                RabbitMessage(
                    body={"user_uuid": user_uuid},
                ),
                exchange="delayed_delete_exchange",
                routing_key="delete_user_route"
            )

    async def send_confirmation_email(self, params: SendConfirmEmailDM) -> None:
        async with self._broker as broker:
            await broker.publish(
                RabbitMessage(
                    body={
                        "message_uuid": params.uuid,
                        "email": params.email,
                        "username": params.username
                    }
                ),
                exchange="send_exchange",
                routing_key="register_confirmation_route"
            )