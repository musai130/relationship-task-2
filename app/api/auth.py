from fastapi import APIRouter

from authentication.fastapi_users import fastapi_users
from authentication.backend import authentication_backend
from config import settings
from authentication.schemas.user import (
    UserRead,
    UserCreate,
)

router = APIRouter(
    prefix=settings.url.auth,
    tags=["Auth"],
)

router.include_router(
    router=fastapi_users.get_auth_router(
        authentication_backend,
    ),
)

router.include_router(
    router=fastapi_users.get_register_router(
        UserRead,
        UserCreate,
    ),
)

router.include_router(
    router=fastapi_users.get_verify_router(UserRead),
)

router.include_router(
    router=fastapi_users.get_reset_password_router(),
)
