"""
Модуль конфигураций.
"""
import typing

from pydantic import BaseSettings, Field


DOC_OPENAPI = '/openapi.json'


class Database(BaseSettings):
    """
    Класс констант для базы данных.
    """
    MAX_LEN_ID: int = 2147483647

    MAX_LEN_USER_LOGIN: int = 20

    MAX_LEN_REPOSITORY_NAME: int = 30

    MAX_LEN_COMMIT_MESSAGE: int = 100

    MIN_LEN_USER_PASSWORD: int = 8
    MAX_LEN_USER_PASSWORD: int = 20

    class Config:
        case_sensitive = True


class Settings(BaseSettings):
    """
    Класс настроек сервера.
    """
    PROJECT_NAME: str
    PROJECT_VERSION: str

    SERVER_HOST: str
    SERVER_PORT: int

    WORKERS: int

    TESTING: bool = Field(default=False)

    OPENAPI: bool = Field(default=False)
    ECHO_DB: bool = Field(default=False)

    LOGGER: bool = Field(default=False)
    LOGS_PATH: str = Field(default='logs')
    LOGS_COUNT: int

    WEB_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int

    SECRET_KEY: str
    ALGORITHM_CRYPTOGRAPHY: str

    AUTH_COOKIES_SECURE: bool = Field(default=True)
    AUTH_COOKIES_HTTP_ONLY: bool = Field(default=True)
    AUTH_COOKIES_SAME_SITE: str = Field(default='none')
    AUTH_COOKIES_DOMAIN: str = Field(default='')

    BACKEND_CORS_ORIGINS: typing.Union[typing.List] = []

    REDIRECT_HTTPS: bool = Field(default=True)

    PATH_TO_USER_DIRECTORIES: str

    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        case_sensitive = True


db_config = Database()
base_config = Settings(_env_file='.env', _env_file_encoding='utf-8')
