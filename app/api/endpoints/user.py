"""
Модуль API user.
"""
import typing

import sqlalchemy as sa
import sqlalchemy.exc
from fastapi import (
    Depends, APIRouter, Path,
    status
)

from app import schemas, models, db
from app.core import security
from app.api import helpers, details
from app.core.config import db_config


router = APIRouter()


@router.post("", response_model=int)
async def create_user(
        data: schemas.UserCreate,
        session: db.AsyncSession = Depends(db.get_session),
        current_user: models.User = Depends(helpers.get_current_user) # noqa
):
    """
    API создания пользователя.
    """
    if data.password != data.confirm_password:
        helpers.abort(code=status.HTTP_400_BAD_REQUEST, detail=details.PASSWORD_DO_NOT_MATCH)

    user = models.User(login=data.login, password=security.get_password_hash(data.password))

    session.add(user)
    try:
        await session.commit()
    except sa.exc.DBAPIError as e:
        await session.rollback()

        helpers.abort(status.HTTP_400_BAD_REQUEST, detail=helpers.error_detail(e))

    return user.id


@router.get("/me", response_model=schemas.UserInDb)
async def get_user_me(current_user: models.User = Depends(helpers.get_current_user)):
    """
    API получения информации о пользователе.
    """
    return current_user


@router.get("", response_model=typing.List[schemas.UserInDb])
async def get_users(
        session: db.AsyncSession = Depends(db.get_session),
        current_user: models.User = Depends(helpers.get_current_user) # noqa
):
    """
    API получения пользователей.
    """
    users = (await session.scalars(sa.select(models.User))).all()

    return users


@router.delete("/{user_id}", response_model=schemas.Status)
async def delete_user(
        user_id: int = Path(..., ge=1, le=db_config.MAX_LEN_ID),
        session: db.AsyncSession = Depends(db.get_session),
        current_user: models.User = Depends(helpers.get_current_user)
):
    """
    API удаления пользователя.
    """
    if user_id == current_user.id:
        helpers.abort(code=status.HTTP_400_BAD_REQUEST, detail=details.YOU_CANNOT_DELETE_YOURSELF)

    user = await session.scalar(sa.select(models.User).where(models.User.id == user_id))
    if not user:
        helpers.abort(code=status.HTTP_404_NOT_FOUND, detail=details.USER_IS_NOT_FOUND)

    try:
        await session.delete(user)
        await session.commit()
    except sa.exc.DBAPIError as e:
        await session.rollback()

        helpers.abort(code=status.HTTP_400_BAD_REQUEST, detail=helpers.error_detail(e))

    return schemas.Status(status='success')
