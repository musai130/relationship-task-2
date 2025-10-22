from typing import Annotated
from fastapi import APIRouter, Depends, status
from schemas import AllergenRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import db_helper, Allergen
from config import settings

router = APIRouter(
    tags=["Allergens"],
    prefix=settings.url.allergen,
)

@router.get("", response_model=list[AllergenRead])
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    stmt = select(Allergen).order_by(Allergen.id)
    allergens = await session.scalars(stmt)
    return allergens.all()

@router.post("", response_model=AllergenRead, status_code=status.HTTP_201_CREATED)
async def store(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    allergen_create: AllergenRead
):
    allergen = Allergen(name=allergen_create.name)
    session.add(allergen)
    await session.commit()
    return allergen

@router.get("/{id}", response_model=AllergenRead)
async def show(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
):
    allergen = await session.get(Allergen, id)
    return allergen

@router.put("/{id}", response_model=AllergenRead)
async def update(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
    allergen_update: AllergenRead
):
    allergen = await session.get(Allergen, id)
    allergen.name = allergen_update.name
    await session.commit()
    return allergen

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
):
    allergen = await session.get(Allergen, id)
    await session.delete(allergen)
    await session.commit()