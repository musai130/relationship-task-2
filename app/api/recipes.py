from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, add_pagination, paginate
from models.cuisine import Cuisine
from models.ingredient import Ingredient
from models.allergen import Allergen
from models.recipe_ingredients import RecipeIngredient
from models import db_helper, Recipe
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas import RecipeCreate, RecipeRead
from sqlalchemy.orm import selectinload
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination.ext.sqlalchemy import paginate as apaginate
from fastapi_filter import with_prefix

router = APIRouter(
    tags=["Recipes"],
    prefix=settings.url.recipe,
)

class RecipeIngredientFilter(Filter):
    ingredient_id: Optional[int] = None

    class Constants(Filter.Constants):
        model = RecipeIngredient

class RecipeFilter(Filter):
    title__like: Optional[str] = None
    recipe_ingredients: Optional[RecipeIngredientFilter] = FilterDepends(
        with_prefix("recipe_ingredients", RecipeIngredientFilter)
    )
    custom_order_by: Optional[list[str]] = ["id", 'difficulty']

    class Constants(Filter.Constants):
        model = Recipe
        ordering_field_name = "custom_order_by"
        search_model_fields = ["title"]




@router.put("/{id}", response_model=RecipeRead)
async def update(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
    recipe_update: RecipeCreate
):
    recipe = await session.get(Recipe, id)
    recipe.title = recipe_update.title
    recipe.description = recipe_update.description
    recipe.cooking_time = recipe_update.cooking_time
    recipe.difficulty = recipe_update.difficulty
    await session.commit()
    return recipe


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    recipe = await session.get(Recipe, id)
    await session.delete(recipe)
    await session.commit()

# @router.get("", response_model=list[RecipeRead])
# async def index(
#     session: Annotated[
#         AsyncSession,
#         Depends(db_helper.session_getter),
#     ],
# ):
#     stmt = (
#         select(Recipe)
#         .options(
#             selectinload(Recipe.cuisine),
#             selectinload(Recipe.allergens),
#             selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient)
#         )
#         .order_by(Recipe.id)
#     )
#     recipes = await session.scalars(stmt)
    
#     valid_recipes = []
#     for recipe in recipes.all():
#         recipe.recipe_ingredients = [
#             ri for ri in recipe.recipe_ingredients 
#             if ri.ingredient is not None
#         ]
#         valid_recipes.append(recipe)
    
#     return valid_recipes

@router.post("", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
async def store(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    recipe_create: RecipeCreate
):
    cuisine = None
    if recipe_create.cuisine_id:
        cuisine = await session.get(Cuisine, recipe_create.cuisine_id)
        if not cuisine:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cuisine with id {recipe_create.cuisine_id} not found"
            )

    allergens = []
    if recipe_create.allergen_ids:
        stmt = select(Allergen).where(Allergen.id.in_(recipe_create.allergen_ids))
        allergens_result = await session.scalars(stmt)
        allergens = allergens_result.all()
        
        if len(allergens) != len(recipe_create.allergen_ids):
            found_ids = {a.id for a in allergens}
            missing_ids = set(recipe_create.allergen_ids) - found_ids
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Allergens with ids {missing_ids} not found"
            )
    ingredient_ids = [ing.ingredient_id for ing in recipe_create.ingredients]
    if ingredient_ids:
        stmt = select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
        ingredients_result = await session.scalars(stmt)
        existing_ingredients = ingredients_result.all()
        
        if len(existing_ingredients) != len(ingredient_ids):
            found_ids = {i.id for i in existing_ingredients}
            missing_ids = set(ingredient_ids) - found_ids
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ingredients with ids {missing_ids} not found"
            )

    recipe = Recipe(
        title=recipe_create.title,
        description=recipe_create.description,
        cooking_time=recipe_create.cooking_time,
        difficulty=recipe_create.difficulty,
        cuisine_id=recipe_create.cuisine_id,
        allergens=allergens
    )

    session.add(recipe)
    await session.flush()

    for ing_data in recipe_create.ingredients:
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ing_data.ingredient_id,
            quantity=ing_data.quantity,
            measurement=ing_data.measurement
        )
        session.add(recipe_ingredient)

    await session.commit()
    await session.refresh(recipe)
    stmt = (
        select(Recipe)
        .where(Recipe.id == recipe.id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient)
        )
    )
    recipe_with_relations = await session.scalar(stmt)
    
    return recipe_with_relations

@router.get("", response_model=Page[RecipeRead])
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    filters: Optional[RecipeFilter] = FilterDepends(RecipeFilter)
):
    stmt = (
        select(Recipe)
        .outerjoin(Recipe.recipe_ingredients)
        .outerjoin(RecipeIngredient.ingredient)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient)
        )
        .distinct()
    )

    if filters:
        stmt = filters.filter(stmt)
        stmt = filters.sort(stmt)

    return await apaginate(session, stmt)

@router.get("/{id}", response_model=RecipeRead)
async def show(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    id: int,
):
    stmt = (
        select(Recipe)
        .where(Recipe.id == id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient)
        )
    )
    recipe = await session.scalar(stmt)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    
    return recipe

add_pagination(router)