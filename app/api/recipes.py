from typing import Annotated, Optional
from fastapi import APIRouter, Depends
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, add_pagination
from fastapi_pagination.ext.sqlalchemy import paginate as apaginate
from models.users import User
from config import settings
from schemas import RecipeCreate, RecipeRead
from queries.recipe_queries import RecipeQueries, RecipeFilter
from service.recipe_service import RecipeService
from authentication.fastapi_users import current_active_user

router = APIRouter(
    tags=["Recipes"],
    prefix=settings.url.recipe,
)


@router.get("", response_model=Page[RecipeRead])
async def index(
    read: Annotated[RecipeQueries, Depends(RecipeQueries)],
    filters: Optional[RecipeFilter] = FilterDepends(RecipeFilter)
):
    return await apaginate(
        conn=read.session,
        query=read.filtered_query(filters) if filters else read.get_recipes_query()
    )


@router.get("/{id}", response_model=RecipeRead)
async def show(
    id: int,
    read: Annotated[RecipeQueries, Depends(RecipeQueries)],
):
    recipe = await read.get_by_id(id)
    return recipe


@router.post("", response_model=RecipeRead, status_code=201)
async def store(
    recipe_create: RecipeCreate,
    service: Annotated[RecipeService, Depends(RecipeService)],
    user: User = Depends(current_active_user)
):
    recipe = await service.create(recipe_create, user)
    return recipe


@router.put("/{recipe_id}", response_model=RecipeRead)
async def update_recipe(
    recipe_id: int,
    recipe_in: RecipeCreate,
    service: Annotated[RecipeService, Depends(RecipeService)],
    user: User = Depends(current_active_user)
):
    recipe = await service.update(recipe_id, recipe_in, user)
    return recipe


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(
    recipe_id: int,
    service: Annotated[RecipeService, Depends(RecipeService)],
    user: User = Depends(current_active_user)
):
    await service.delete(recipe_id, user)
    return None


add_pagination(router)
