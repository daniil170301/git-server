"""
Модуль API auth.
"""
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import Depends, APIRouter, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core import security
from app import db, models, schemas
from app.api import helpers, details
from app.core.security import base_config


router = APIRouter()


@router.post('/login', response_model=schemas.AccessToken)
async def login(
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: db.AsyncSession = Depends(db.get_session)
):
    """
    API авторизации клиента.
    """
    user = await helpers.authenticate_user(
        login=form_data.username,
        password=form_data.password,
        session=session
    )
    if not user:
        helpers.abort(status.HTTP_400_BAD_REQUEST, detail=details.INCORRECT_USERNAME_OR_PASSWORD_ENTERED)

    response.set_cookie(
        key="refresh_token",
        value=security.create_token(subject=user, is_refresh=True),
        expires=base_config.REFRESH_TOKEN_EXPIRE_MINUTES,
        secure=base_config.AUTH_COOKIES_SECURE,
        httponly=base_config.AUTH_COOKIES_HTTP_ONLY,
        samesite=base_config.AUTH_COOKIES_SAME_SITE,
        domain=base_config.AUTH_COOKIES_DOMAIN
    )

    return {
        "access_token": security.create_token(subject=user),
        "token_type": "bearer"
    }


@router.post("/logout", response_model=schemas.Status)
async def logout(
        response: Response,
        request: Request
):
    """
    API завершения сеанса.
    """
    refresh_token = request.cookies.get('refresh_token', None)
    if not refresh_token:
        helpers.abort(status.HTTP_403_FORBIDDEN, detail=details.AUTHORIZATION_REQUIRED)

    response.delete_cookie(key='refresh_token')

    return schemas.Status(status='success')


@router.get('/token', response_model=schemas.AccessToken)
async def update_access_token(
        refresh_token: str = Depends(security.refresh_token_manager),
        session: db.AsyncSession = Depends(db.get_session)
):
    """
    API обновления токена доступа.
    """
    if not refresh_token:
        helpers.abort(status.HTTP_400_BAD_REQUEST, detail=details.AUTHORIZATION_REQUIRED)

    payload = security.decode_token(refresh_token)

    user_id = payload.get('sub')
    aud = payload.get('aud')

    user = await session.get(models.User, user_id)
    if not user:
        helpers.abort(status.HTTP_401_UNAUTHORIZED, detail=details.USER_IS_NOT_FOUND)

    return {
        "access_token": security.create_token(subject=user, aud=aud),
        "token_type": "bearer",
    }
