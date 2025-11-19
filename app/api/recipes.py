from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi_filter import FilterDepends
from fastapi_pagination import Page, add_pagination, paginate
from models.users import User
from models.cuisine import Cuisine
from models.ingredient import Ingredient
from models.allergen import Allergen
from models.recipe_ingredients import RecipeIngredient, MeasurementEnum
from models import db_helper, Recipe
from config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas import RecipeCreate, RecipeRead
from sqlalchemy.orm import selectinload
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_pagination.ext.sqlalchemy import paginate as apaginate
from fastapi_filter import with_prefix
from authentication.fastapi_users import current_active_user

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


def parse_measurement(measurement_str: str) -> MeasurementEnum:
    """Преобразует строку в MeasurementEnum"""
    measurement_lower = measurement_str.lower().strip()
    
    if measurement_lower in ['g', 'г', 'grams', 'gram', 'граммы', 'грамм']:
        return MeasurementEnum.GRAMS

    if measurement_lower in ['шт', 'pieces', 'piece', 'pcs', 'pc', 'штуки', 'штука']:
        return MeasurementEnum.PIECES
    
    if measurement_lower in ['ml', 'мл', 'milliliters', 'milliliter', 'миллилитры', 'миллилитр']:
        return MeasurementEnum.MILLILITERS
    
    try:
        return MeasurementEnum[measurement_str.upper()]
    except (KeyError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid measurement value: '{measurement_str}'. Allowed values: 'g'/'г' (grams), 'шт'/'pieces' (pieces), 'ml'/'мл' (milliliters)"
        )




@router.put("/{recipe_id}", response_model=RecipeRead)
async def update_recipe(
    recipe_id: int,
    recipe_in: RecipeCreate,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: User = Depends(current_active_user)
):
    stmt = (
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.author)
        )
    )
    recipe = await session.scalar(stmt)
    
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    if recipe.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the author of this recipe"
        )
    
    recipe.title = recipe_in.title
    recipe.description = recipe_in.description
    recipe.cooking_time = recipe_in.cooking_time
    recipe.difficulty = recipe_in.difficulty
    
    if recipe_in.cuisine_id:
        cuisine = await session.get(Cuisine, recipe_in.cuisine_id)
        if not cuisine:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cuisine with id {recipe_in.cuisine_id} not found"
            )
        recipe.cuisine = cuisine
    else:
        recipe.cuisine = None
    
    allergens = []
    if recipe_in.allergens:
        stmt = select(Allergen).where(Allergen.id.in_(recipe_in.allergens))
        allergens_result = await session.scalars(stmt)
        allergens = allergens_result.all()
        
        if len(allergens) != len(recipe_in.allergens):
            found_ids = {a.id for a in allergens}
            missing_ids = set(recipe_in.allergens) - found_ids
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Allergens with ids {missing_ids} not found"
            )
    recipe.allergens = allergens
    
    ingredient_ids = [ing.ingredient_id for ing in recipe_in.ingredients]
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

    stmt_old_ingredients = select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
    old_ingredients_result = await session.scalars(stmt_old_ingredients)
    old_ingredients = old_ingredients_result.all()
    for old_ingredient in old_ingredients:
        await session.delete(old_ingredient)
    
    for ing_data in recipe_in.ingredients:
        measurement_enum = parse_measurement(ing_data.measurement)
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ing_data.ingredient_id,
            quantity=ing_data.quantity,
            measurement=measurement_enum
        )
        session.add(recipe_ingredient)
    
    await session.commit()
    
    stmt = (
        select(Recipe)
        .where(Recipe.id == recipe.id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.author)
        )
    )
    recipe_with_relations = await session.scalar(stmt)
    
    return recipe_with_relations


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: int,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: User = Depends(current_active_user)
):
    recipe = await session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipe not found"
        )
    if recipe.author_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the author of this recipe"
        )
    
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
    recipe_create: RecipeCreate,
    user: User = Depends(current_active_user)
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
    if recipe_create.allergens:
        stmt = select(Allergen).where(Allergen.id.in_(recipe_create.allergens))
        allergens_result = await session.scalars(stmt)
        allergens = allergens_result.all()
        
        if len(allergens) != len(recipe_create.allergens):
            found_ids = {a.id for a in allergens}
            missing_ids = set(recipe_create.allergens) - found_ids
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
        allergens=allergens,
        author_id=user.id
    )

    session.add(recipe)
    await session.flush()

    for ing_data in recipe_create.ingredients:
        measurement_enum = parse_measurement(ing_data.measurement)
        recipe_ingredient = RecipeIngredient(
            recipe_id=recipe.id,
            ingredient_id=ing_data.ingredient_id,
            quantity=ing_data.quantity,
            measurement=measurement_enum
        )
        session.add(recipe_ingredient)

    await session.commit()
    stmt = (
        select(Recipe)
        .where(Recipe.id == recipe.id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.author)
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
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.author)
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
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient),
            selectinload(Recipe.author)
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