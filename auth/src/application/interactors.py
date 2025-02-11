from typing import Optional, Any
import json
from redis.asyncio import Redis

from sqlalchemy import Row
from litestar.security.jwt.auth import OAuth2Login

import interfaces
import dto
from src.domain import entities

class SignupInteractor:
    def __init__(
        self,
        db_session: interfaces.DBSession,
        signup_gateway: interfaces.SignupInterface,
    ) -> None:
        self._db_session = db_session
        self._signup_gateway = signup_gateway

    async def __call__(self, data: entities.SaveUserDM) -> None:
        await self._signup_gateway.signup(data)
        await self._db_session.commit()


class SaltGeneratorInteractor:
    def __init__(
        self,
        generator_gateway: interfaces.SaltGeneratorInterface
    ) -> None:
        self._generator_gateway = generator_gateway

    async def __call__(self) -> str:
        return await self._generator_gateway.generate_salt()


class HashPasswordInteractor:
    def __init__(
        self,
        hash_gateway: interfaces.PasswordHasherInterface
    ) -> None:
        self._hash_gateway = hash_gateway

    async def __call__(self, dto: dto.HashPasswordDTO) -> str:
        data = entities.HashPasswordMethodDM(
            password = dto.password,
            salt = dto.salt
        )
        return await self._hash_gateway.hash_password_with_salt(data)


class LoadUserFromCacheInteractor:
    def __init__(
        self,
        redis_client: Redis
    ) -> None:
        self._redis_client=redis_client

    async def __call__(self, dto: dto.TokenDTO) -> Optional[entities.SaveUserDM]:
        token_dm = entities.TokenDM(token=dto.token)
        temp_user_data = await self._redis_client.get(token_dm.token)
        if temp_user_data is None:
            return None
        user:dict = json.loads(temp_user_data)
        return entities.SaveUserDM(
            uuid=user["uuid"],
            username=user["username"],
            firstname=user["firstname"],
            lastname=user["lastname"],
            email=user["email"],
            hashed_password=user["hashed_password"],
            salt=user["salt"]
        )


class DeleteUserFromCacheInteractor:
    def __init__(
        self,
        redis_client: Redis
    ) -> None:
        self._redis_client=redis_client

    async def __call__(self, dto: dto.TokenDTO) -> None:
        token_dm = entities.TokenDM(token=dto.token)
        await self._redis_client.delete(f'user_{token_dm.token}')


class SaveUserCacheInteractor:
    def __init__(
        self,
        redis_client: Redis
    ) -> None:
        self._redis_client = redis_client

    async def __call__(self, dto: dto.UserCacheDTO) -> None:
        user_cache_dm = entities.SaveUserCacheDM(
            username=dto.username,
            firstname=dto.firstname,
            lastname=dto.lastname,
            email=dto.email,
            hashed_password=dto.hashed_password,
            salt=dto.salt
        )
        await self._redis_client.setex(name=f'user_{dto.token}',
            value=user_cache_dm.model_dump_json())


class CreateNewUserInteractor:
    def __init__(
            self,
            user_gateway: interfaces.CreateNewUserInterface,
            uuid_generator: interfaces.UUIDGenerator,
    ) -> None:
        self._user_gateway = user_gateway
        self._uuid_generator = uuid_generator

    async def __call__(self, dto: dto.NewUserDTO) -> Optional[Row[Any]]:
        uuid = str(self._uuid_generator())
        user = entities.NewUserDM(
            uuid=uuid,
            username=dto.username,
            firstname=dto.firstname,
            lastname=dto.lastname,
            email=dto.email,
            password=dto.password
        )
        return await self._user_gateway.create_new_user(user)


class VerifyTokenInteractor:
    def __init__(
        self,
        verify_gateway: interfaces.VerifyTokenInterface,
    ) -> None:
        self._verify_gateway = verify_gateway

    async def __call__(self, dto: dto.TokenDTO) -> Optional[str]:
        token = entities.TokenDM(token = dto.token)
        return await self._verify_gateway.verify_token(token)


class CreateRefreshTokenInteractor:
    def __init__(
        self,
        create_gateway: interfaces.CreateRefreshTokenInterface
    ) -> None:
        self._create_gateway = create_gateway

    async def __call__(self, dto: dto.AccessRefreshTokenDTO) -> str:
        data = entities.AccessRefreshTokenDM(
            data=dto.data,
            expires_timedelta=dto.expires_timedelta
        )
        return await self._create_gateway.create_refresh_token(data)


class CreateAccessTokenInteractor:
    def __init__(
        self,
        create_gateway: interfaces.CreateAccessTokenInterface
    ) -> None:
        self._create_gateway = create_gateway

    async def __call__(self, dto: dto.AccessRefreshTokenDTO) -> str:
        config = entities.AccessRefreshTokenDM(
            data=dto.data,
            expires_timedelta=dto.expires_timedelta
        )
        return await self._create_gateway.create_access_token(config)


class GetUserDataInteractor:
    def __init__(
        self,
        user_gateway: interfaces.GetUserDataInterface
    ) -> None:
        self._user_gateway = user_gateway

    async def __call__(self, form_data: OAuth2Login) -> entities.UserDataDM:
        return await self._user_gateway.get_user_data(form_data)