"""
Модуль модели коммитов.
"""
import typing

import sqlalchemy as sa
import sqlalchemy.orm

from app import db
from app.core.config import db_config


if typing.TYPE_CHECKING:
    from .repository import Repository, RepositoryUser


class Commit(db.Base):
    """Модель таблицы коммитов.

    :id: Уникальный идентификатор таблицы.

    :repository_id: Идентификатор репозитория.

    :date: Время создания коммита.
    :message: Комментарий к коммиту.

    :repository_user_id: Идентификатор пользователя репозитория.
    """
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)

    repository_id = sa.Column(sa.Integer, sa.ForeignKey('repository.id'), nullable=False)

    date = sa.Column(sa.DateTime, nullable=False)
    message = sa.Column(sa.String(db_config.MAX_LEN_COMMIT_MESSAGE), nullable=False)

    repository_user_id = sa.Column(sa.Integer, sa.ForeignKey('repository_user.id'), nullable=False)

    repository: "Repository" = sa.orm.relationship('Repository', lazy='raise_on_sql', uselist=False)
    repository_user: "RepositoryUser" = sa.orm.relationship('RepositoryUser', lazy='raise_on_sql', uselist=False)

    def __str__(self):
        return f'commit-{self.id}'

    def __repr__(self):
        return f'commit-{self.id}'


class File(db.Base):
    """Модель таблицы файлов репозитория.

    :id: Уникальный идентификатор таблицы.

    :repository_id: Идентификатор репозитория.

    :path: Путь к файлу.
    """
    id = sa.Column(sa.Integer, primary_key=True, nullable=False)

    repository_id = sa.Column(sa.Integer, sa.ForeignKey('repository.id'), nullable=False)

    path = sa.Column(sa.String, nullable=False)

    repository: "Repository" = sa.orm.relationship('Repository', lazy='raise_on_sql', uselist=False)

    def __str__(self):
        return f'file-{self.id}'

    def __repr__(self):
        return f'file-{self.id}'


class CommitFileChanges(db.Base):
    """Модель таблицы изменений файлов.

    :id: Уникальный идентификатор таблицы.

    :repository_id: Идентификатор репозитория.

    :date: Время создания коммита.
    :message: Комментарий к коммиту.

    :repository_user_id: Идентификатор пользователя репозитория.
    """
    commit_id = sa.Column(sa.Integer, sa.ForeignKey('commit.id'), primary_key=True, nullable=False)

    last_file_id = sa.Column(sa.Integer, sa.ForeignKey('file.id'), primary_key=True, nullable=False)
    new_file_id = sa.Column(sa.Integer, sa.ForeignKey('file.id'), primary_key=True, nullable=False)

    commit: "Commit" = sa.orm.relationship('Commit', lazy='raise_on_sql', uselist=False)
    last_file: "File" = sa.orm.relationship(
        'File',
        lazy='raise_on_sql',
        foreign_keys=[last_file_id],
        primaryjoin='CommitFileChanges.last_file_id == File.id',
        uselist=False
    )
    new_file: "File" = sa.orm.relationship(
        'File',
        lazy='raise_on_sql',
        foreign_keys=[new_file_id],
        primaryjoin='CommitFileChanges.new_file_id == File.id',
        uselist=False
    )

    def __str__(self):
        return f'{self.last_file_id} -> {self.new_file_id}'

    def __repr__(self):
        return f'{self.last_file_id} -> {self.new_file_id}'
