from typing import Optional
from datetime import timedelta

from pydantic import BaseModel
from fastapi_mail import FastMail


class UserBase(BaseModel):
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: str


class NewUserDM(UserBase):
    uuid: str
    password: str


class SaveUserCacheDM(UserBase):
    token: Optional[str] = None
    hashed_password: str
    salt: str


class SaveUserDM(UserBase):
    uuid: str
    hashed_password: str
    salt: str
    is_active: bool = True


class TokenDM(BaseModel):
    token: str


class AccessRefreshTokenDM(BaseModel):
    data: dict
    expires_timedeta: Optional[timedelta] = None 


class HashPasswordMethodDM(BaseModel):
    password: str
    salt: str


class MailSenderDM(BaseModel):
    fm: FastMail
    email: str
    username: str
    token: str


class UserDataDM(BaseModel):
    username: str
    email: str
    hashed_password: str
    salt: str
    is_active: bool


class AuthForm(BaseModel):
    username: str
    password: str