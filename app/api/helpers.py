"""
Модуль дополнительных функций.
"""
import re
import typing

import sqlalchemy as sa
import sqlalchemy.exc
from fastapi import (
    HTTPException, status, Depends,
    Header
)

from app import models, db
from app.api import details
from app.core import security


def abort(code: int, detail: str = None) -> None:
    """Функция вызывает HTTPException.

    :param code: Код ошибки.
    :param detail: Сообщение об ошибке.
    """
    if code == 403 and not detail:
        detail = details.NOT_ENOUGH_PERMISSIONS

    raise HTTPException(status_code=code, detail=detail)


def error_detail(e: sa.exc.DBAPIError) -> str:
    """
    Функция получения описания ошибки.

    :param e: Exception

    :return: описание ошибки
    """
    message = e.args[0]

    field = re.search('Key \((.*)\)=\(.+\)', message, re.DOTALL | re.IGNORECASE)
    fields = field.group(1).split(', ') if field else ''

    fields_error = ''

    for i, clm in enumerate(fields):
        fields_error += clm.upper()
        if i != len(fields) - 1:
            fields_error += '_AND_'

    if 'already exists' in message:
        error = f'{fields_error}_ALREADY_EXISTS'
    elif 'is not present in table' in message:
        error = f'{fields_error}_NOT_EXISTS'
    elif 'invalid input value for enum' in message:
        error = f'INVALID_INPUT_VALUE_FOR_ENUM'
    else:
        error = 'UNKNOWN_ERROR'

    return error


async def authenticate_user(
        login: str,
        password: str,
        session: db.AsyncSession = Depends(db.get_session)
) -> typing.Union[models.User, bool]:
    """
    Функция аутентификации пользователя по логину и паролю.

    :param login: Логин пользователя.
    :param password: Пароль пользователя.
    :param session: Сессия.

    :return: models.User
    """
    user = await session.scalar(sa.select(models.User).where(models.User.login == login))
    if not user:
        return False
    elif not security.verify_password(password, user.password):
        return False

    return user


class UserActive:

    def __init__(self, is_none: bool = False):
        self.is_none = is_none

    async def __call__(
            self,
            client_name: typing.Optional[str] = Header(None, alias='Client_name'),
            token: str = Depends(security.login_manager),
            session: db.AsyncSession = Depends(db.get_session)
    ) -> typing.Optional[models.User]:
        """Функция возвращает объект пользователя.
        В случае неудачи будет вызвана ошибка.

        :param client_name: Имя клиента.
        :param token: Токен доступа.
        :param session: Сессия базы данных.

        :return: models.User.
        """
        if not token and not self.is_none:
            abort(code=status.HTTP_401_UNAUTHORIZED, detail=details.AUTHORIZATION_REQUIRED)

        user = None
        if token:
            payload = security.decode_token(token)
            user = await session.scalar(sa.select(models.User).where(models.User.id == payload.get('sub')))

            if not user:
                abort(code=status.HTTP_401_UNAUTHORIZED, detail=details.USER_IS_NOT_FOUND)

            session.expunge(user)

        return user


get_current_user = UserActive()
get_current_user_or_none = UserActive(is_none=True)
