"""
Модуль модели репозиториев.
"""
import typing
from enum import Enum

import sqlalchemy as sa
import sqlalchemy.orm

from app import db
from app.core.config import db_config


if typing.TYPE_CHECKING:
    from .user import User, UserDirectory


class Repository(db.Base):
    """Модель таблицы репозиториев.

    :id: Уникальный идентификатор таблицы.

    :user_directory_id: Идентификатор директории пользователя.
    :name: Название.
    """
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)

    user_directory_id = sa.Column(sa.Integer, sa.ForeignKey('user_directory.id'), nullable=False)
    name = sa.Column(sa.String(db_config.MAX_LEN_REPOSITORY_NAME), nullable=False)

    user_directory: "UserDirectory" = sa.orm.relationship('UserDirectory', lazy='raise_on_sql', uselist=False)

    def __str__(self):
        return f'{self.name} - user{self.user_directory_id}'

    def __repr__(self):
        return f'{self.name} - user{self.user_directory_id}'


class Role(Enum):
    """Список ролей пользователя"""
    OWNER = 1
    MAINTAINER = 2
    DEVELOPER = 3
    REPORTER = 4
    GUEST = 5


class RepositoryUser(db.Base):
    """Модель таблицы пользователей репозитория.

    :id: Уникальный идентификатор таблицы.

    :user_id: Идентификатор пользователя.

    :repository_id: Идентификатор репозитория.

    :role: Роль пользователя.
    """
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)

    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    repository_id = sa.Column(sa.Integer, sa.ForeignKey('repository.id'), nullable=False)

    role = sa.Column(sa.Enum(Role), nullable=False, default=Role.GUEST)

    user: "User" = sa.orm.relationship('User', lazy='raise_on_sql', uselist=False)
    repository: "Repository" = sa.orm.relationship('Repository', lazy='raise_on_sql', uselist=False)

    __table_args__ = (sa.UniqueConstraint('user_id', 'repository_id', name='_repository_user_uc'),)

    def __str__(self):
        return self.user_id

    def __repr__(self):
        return self.user_id
