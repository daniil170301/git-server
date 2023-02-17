"""
Скрипт заполнения БД основными данными.
"""
import os
import sys
import inspect

from sqlalchemy.ext.asyncio import async_scoped_session

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

import asyncio

from app import models
from app.core import security
from app.db.session import Session
from app.core.config import base_config


session = async_scoped_session(Session, scopefunc=asyncio.current_task)


async def insert_users():
    user = models.User(login='admin', password=security.get_password_hash('admin'))
    session.add(user)

    await session.flush()

    user_directory_path = f'{base_config.PATH_TO_USER_DIRECTORIES}/{user.id}'

    os.makedirs(user_directory_path)
    user_directory = models.UserDirectory(user_id=user.id, path=user_directory_path)
    session.add(user_directory)

    await session.commit()

    print('Администратор успешно добавлен!')


async def main():
    await insert_users()
    await session.close()


if __name__ == '__main__':
    asyncio.run(main())
