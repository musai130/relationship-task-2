from typing import Annotated
from fastapi import APIRouter, Depends, status
from schemas import CuisineCreate, CuisineRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import db_helper, Cuisine
from config import settings

router = APIRouter(
    tags=["Cuisines"],
    prefix=settings.url.cuisine,
)

@router.get("", response_model=list[CuisineRead])
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    stmt = select(Cuisine).order_by(Cuisine.id)
    cuisines = await session.scalars(stmt)
    return cuisines.all()

@router.post("", response_model=CuisineRead, status_code=status.HTTP_201_CREATED)
async def store(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    cuisine_create: CuisineCreate
):
    cuisine = Cuisine(name=cuisine_create.name)
    session.add(cuisine)
    await session.commit()
    return cuisine

@router.get("/{id}", response_model=CuisineRead)
async def show(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
):
    cuisine = await session.get(Cuisine, id)
    return cuisine

@router.put("/{id}", response_model=CuisineRead)
async def update(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
    cuisine_update: CuisineCreate
):
    cuisine = await session.get(Cuisine, id)
    cuisine.name = cuisine_update.name
    await session.commit()
    return cuisine

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
):
    cuisine = await session.get(Cuisine, id)
    await session.delete(cuisine)
    await session.commit()