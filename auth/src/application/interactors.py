from typing import Optional

from argon2 import PasswordHasher

from auth.src.application.interfaces import (
    DBSession, 
    DeleteUserTask, 
    SendConfirmationEmail, 
    UUIDGenerator, 
    Auth, 
    RedisService,
    Cruds
)
from auth.src.application.dto import (
    LoginDTO, 
    SignupDTO, 
    TokensDTO
)
from auth.src.config import AppConfig
from auth.src.domain.entities import (
    DeleteUserTaskDM,
    GetUserDM, 
    RevokeTokenDM, 
    RevokeTokensDM, 
    SendConfirmEmailDM, 
    TokenDM, 
    UserDataDM, 
    UserDM
)


class SignupInteractor:
    def __init__(
        self,
        config: AppConfig,
        uuid_generator: UUIDGenerator,
        hasher: PasswordHasher,
        cache_gateway: RedisService,
        task_gateway: DeleteUserTask,
        email_gateway: SendConfirmationEmail,
    ) -> None:
        self._config = config
        self._uuid_generator = uuid_generator
        self._hasher = hasher
        self._cache_gateway = cache_gateway
        self._task_gateway = task_gateway
        self._email_gateway = email_gateway

    async def __call__(self, params: SignupDTO) -> UserDataDM:
        new_user_uuid = self._uuid_generator()
        hashed_password = self._hasher.hash(
            params.password + self._config.secret_key
        )
        user_dm = UserDM(
            uuid=new_user_uuid,
            firstname=params.firstname,
            lastname=params.lastname,
            username=params.username or params.email,
            email=params.email,
            phone_number=params.phone or None,
            hashed_password=hashed_password,
            is_active=False,
        )
        await self._cache_gateway.save_user(user_dm)
        delete_user_dm = DeleteUserTaskDM(user_uuid=new_user_uuid)
        await self._task_gateway.schedule_user_deletion(delete_user_dm)
        send_mail_dm = SendConfirmEmailDM(
            uuid=new_user_uuid,
            email=params.email,
            username=params.username or params.email
        )
        await self._email_gateway.send_confirmation_email(send_mail_dm)
        return UserDataDM(**user_dm)


class ConfirmSignupInteractor:
    def __init__(
        self,
        cache_gateway: RedisService,
        signup_gateway: Cruds,
        db_session: DBSession,
        auth_gateway: Auth,
    ) -> None:
        self._cache_gateway = cache_gateway
        self._signup_gateway = signup_gateway
        self._db_session = db_session
        self._auth_gateway = auth_gateway

    async def __call__(self, user_uuid: str) -> TokenDM:
        await self._cache_gateway.cancel_shedule_user_deletion(user_uuid)
        user_dm = await self._cache_gateway.load_user(user_uuid=user_uuid)
        await self._cache_gateway.delete_user(user_uuid=user_uuid)
        new_user_dm = await self._signup_gateway.signup(user_dm)
        await self._db_session.commit()
        access_token = await self._auth_gateway.create_access_token(new_user_dm)
        refresh_token= await self._auth_gateway.create_refresh_token(new_user_dm)
        return TokenDM(
            access_token=access_token,
            refresh_token=refresh_token
        )


class LoginInteractor:
    def __init__(
        self,
        config: AppConfig,
        cache_gateway: RedisService,
        user_gateway: Cruds,
        hasher: PasswordHasher,
        db_session: DBSession,
        auth_gateway: Auth,
    ) -> None:
        self._config = config
        self._cache_gateway = cache_gateway
        self._user_gateway = user_gateway
        self._hasher = hasher
        self._db_session = db_session
        self._auth_gateway = auth_gateway


    async def __call__(self, params: LoginDTO) -> Optional[TokenDM]:
        get_user_dm = GetUserDM(**params)
        user_password_dm = await self._user_gateway.get_user_data(get_user_dm)
        if not user_password_dm or not user_password_dm.is_active:
            return None
        hashed_password = self._hasher.hash(
            params.password + self._config.secret_key
        )
        if hashed_password == user_password_dm.hashed_password:
            user_dm = UserDM(**user_password_dm)
            access_token = await self._auth_gateway.create_access_token(user_dm)
            refresh_token= await self._auth_gateway.create_refresh_token(user_dm)
            return TokenDM(
                access_token=access_token,
                refresh_token=refresh_token
            ) 
        return None


class RefreshTokenInteractor:
    def __init__(
        self,
        cache_gateway: RedisService,
        auth_gateway: Auth
    ) -> None:
        self._cache_gateway = cache_gateway
        self._auth_gateway = auth_gateway

    async def __call__(self, params: TokensDTO) -> Optional[TokenDM]:
        token_dm = RevokeTokenDM(token=params.refresh_token, token_type="refresh")
        if await self._cache_gateway.is_token_revoked(token_dm):
            user_dm = await self._auth_gateway.verify_refresh_token(params.refresh_token)
            if not user_dm:
                return None
            new_access_token = await self._auth_gateway.create_access_token(user_dm)
            return TokenDM(
                access_token=new_access_token,
                refresh_token=params.refresh_token
            )
        return None


class VerifyTokenInteractor:
    def __init__(
        self,
        verify_gateway: Auth,
        cache_gateway: RedisService,
    ) -> None:
        self._verify_gateway = verify_gateway
        self._cache_gateway = cache_gateway

    async def __call__(self, token: str) -> Optional[UserDataDM]:
        params = RevokeTokenDM(token=token, token_type="access")
        if await self._cache_gateway.is_token_revoked(params):
            return await self._verify_gateway.verify_access_token(token)
        return None


class LogoutInteractor:
    def __init__(
        self,
        cache_gateway: RedisService,
        auth_gateway: Auth,
    ) -> None:
        self._cache_gateway = cache_gateway
        self._auth_gateway = auth_gateway

    async def __call__(self, params: TokensDTO) -> Optional[bool]:
        access_data = await self._auth_gateway.verify_access_token(params.access_token)
        refresh_data = await self._auth_gateway.verify_refresh_token(params.refresh_token)
        if not access_data or not refresh_data:
            return None
        access_exp = access_data.exp
        refresh_exp = refresh_data.exp
        revoke_dm = RevokeTokensDM(
            access_token=params.access_token,
            access_exp=access_exp,
            refresh_token=params.refresh_token,
            refresh_exp=refresh_exp
        )
        return await self._cache_gateway.save_revoked_tokens(revoke_dm)