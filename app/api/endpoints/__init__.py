"""
Модуль импорта маршрутов API.
"""
from fastapi import APIRouter

from app.api.endpoints import auth, user


api_router = APIRouter(prefix='/api')

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["user"])
