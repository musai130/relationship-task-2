from typing import Optional
from fastapi_users import schemas
from pydantic import Field


class UserRead(schemas.BaseUser[int]):
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserCreate(schemas.BaseUserCreate):
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")


class UserUpdate(schemas.BaseUserUpdate):
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
