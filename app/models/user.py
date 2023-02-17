"""
Модуль модели пользователя.
"""
import sqlalchemy as sa
import sqlalchemy.orm

from app import db
from app.core.config import db_config


class User(db.Base):
    """Модель таблицы пользователей.

    :id: Уникальный идентификатор таблицы.

    :login: Логин.
    :password: Пароль.

    :created: Дата и время создания пользователя.
    """
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)

    login = sa.Column(sa.String(db_config.MAX_LEN_USER_LOGIN), nullable=False, unique=True)
    password = sa.Column(sa.String, nullable=False)

    created = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())

    user_directory: "UserDirectory" = sa.orm.relationship(
        'UserDirectory',
        lazy='raise_on_sql',
        viewonly=True,
        uselist=False
    )

    def __str__(self):
        return self.login

    def __repr__(self):
        return self.login


class UserDirectory(db.Base):
    """Модель таблицы директорий пользователей.

    :id: Уникальный идентификатор таблицы.

    :user_id: Уникальный идентификатор пользователя.

    :path: Путь.
    """
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False, unique=True)

    path = sa.Column(sa.String, nullable=False, unique=True)

    def __str__(self):
        return self.path

    def __repr__(self):
        return self.path
