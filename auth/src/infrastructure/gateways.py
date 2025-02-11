import os
import hashlib
from datetime import timedelta, datetime, timezone
from typing import Optional, Any

from jose import JWTError, jwt
from litestar.security.jwt.auth import OAuth2PasswordBearerAuth
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from src.config import SecurityConfig
from src.application import interactors
from src.domain import entities


class SignupGateway(interactors.SignupInteractor):
    def __init__(
        self,
        session_db: AsyncSession
    ) -> None:
        self._session_db = session_db

    async def signup(self, data: entities.SaveUserDM) -> None:
        query = sa.text("""
            INSERT INTO user_users 
                (uuid, email, username, firstname,
                lastname, salt, hashed_password, is_active)
            VALUES
                (:uuid, :email, :username, :firstname,
                :lastname, :salt, :hashed_password, :is_active)
        """)
        await self._session_db.execute(
            statement=query,
            params = data.model_dump()
        )


class GenerateSaltGateway(interactors.SaltGeneratorInteractor):
    async def generate_salt() -> str:
        return os.urandom(16).hex()


class HashPasswordGateway(interactors.HashPasswordInteractor):
    async def hash_password_with_salt(self, data: entities.HashPasswordMethodDM) -> str:
        password_bytes = data.password.encode('utf-8')
        salt_bytes = data.salt.encode('utf-8')
        return hashlib.sha256(password_bytes + salt_bytes).hexdigest()


class CreateAcsessTokenGateway(interactors.CreateNewUserInteractor):
    def __init__(self, config: SecurityConfig) -> None:
        self._config = config

    async def create_access_token(self, data: entities.AccessRefreshTokenDM) -> str:
        to_encode = data.data.copy()
        if expires_delta := data.expires_timedeta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self._config.access_token_expire_minutes
            )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self._config.key, algorithm=self._config.algorithm)



class CreateRefreshTokenGateway(interactors.CreateRefreshTokenInteractor):
    def __init__(
        self,
        config: SecurityConfig
    ) -> None:
        self._config = config

    async def create_refresh_token(self, data: entities.AccessRefreshTokenDM) -> str:
        to_encode = data.data.copy()
        if expires_delta := data.expires_timedeta:
            expire = datetime.now(timezone.utc) + timedelta(days=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=self._config.refresh_access_toksen_expire_days
            )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self._config.key, algorithm=self._config.algorithm)


class VerifyTokenGateway(interactors.VerifyTokenInteractor):
    def __init__(
        self,
        config: SecurityConfig
    ) -> None:
        self._config = config

    async def verify_token(self, token: entities.TokenDM) -> Optional[str]:
        try:
            payload = jwt.decode(
                token = token.token,
                key = self._config.secret_key,
                algorithms = [self._config.algorithm]
            )
            return payload["username"]
        except JWTError as e:
            return None


class CreateNewUserGateway(interactors.CreateNewUserInteractor):
    def __init__(
        self,
        session_db: AsyncSession,
    ) -> None:
        self._session_db = session_db

    async def create_new_user(self, user: entities.NewUserDM) -> Optional[sa.Row[Any]]:
        query = sa.text("""
            SELECT * FROM users 
            WHERE username = :username AND email = :email
        """)
        result = await self._session_db.execute(
            statement = query, 
            params = {
                "username": user.username,
                "email": user.email
            }
        )
        return result.fetchone()


class GetUserDataGateway(interactors.GetUserDataInteractor):
    def __init__(
        self,
        session_db: AsyncSession,
    ) -> None:
        self._session_db = session_db

    async def get_user_data(
        self,
        form_data: OAuth2PasswordBearerAuth
    ) -> Optional[entities.UserDataDM]:
        query = sa.text("SELECT * FROM users WHERE username = :username")
        result = await self._session_db.execute(
            statement=query,
            params={
                "username": form_data.username
            }
        )
        result = result.fetchone()
        if result is None:
            return result
        return entities.UserDataDM(
            username = result["username"],
            email = result["email"],
            hashed_password = result["hashed_password"],
            salt = result["salt"],
            is_active = result["is_active"]
        )