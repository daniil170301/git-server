"""
Модуль схем пользователя.
"""
from pydantic import Field, validator

from app.api import details
from app.core import security
from app.schemas.base import APIBase
from app.core.config import db_config


class UserInDb(APIBase):
    id: int

    login: str


class UserPasswordBase(APIBase):
    password: str = Field(...)

    confirm_password: str = Field(...)


class UserPassword(UserPasswordBase):
    password: str = Field(..., min_length=db_config.MIN_LEN_USER_PASSWORD, max_length=db_config.MAX_LEN_USER_PASSWORD)

    @validator('password')
    def valid_password(cls, value) -> str:
        if not security.password_regex.match(value):
            raise ValueError(details.PASSWORD_FAIL_CONDITIONS)

        return value


class UserChangePassword(UserPassword):
    current_password: str = Field(...)


class UserCreate(UserPasswordBase):
    login: str = Field(..., max_length=db_config.MAX_LEN_USER_LOGIN)


class UserUpdate(APIBase):
    login: str = Field(None, max_length=db_config.MAX_LEN_USER_LOGIN)
