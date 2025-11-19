from typing import Annotated, List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from models.recipe import Recipe
from models.recipe_ingredients import RecipeIngredient
from schemas import IngredientRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select as sql_select
from sqlalchemy.orm import selectinload
from models import db_helper, Ingredient
from config import settings

router = APIRouter(
    tags=["Ingredients"],
    prefix=settings.url.ingredient,
)


@router.get("/{ingredient_id}/recipes", response_model=List[Dict[str, Any]])
async def get_recipes_by_ingredient(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    ingredient_id: int,
    include: Optional[str] = Query(None, description="cuisine,ingredients,allergens"),
    select: Optional[str] = Query(None, description="id,title,description,difficulty,cooking_time"),
):
    ingredient = await session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found"
        )

    includes = [i.strip() for i in (include or "").split(",") if i.strip()]
    basic_fields = ["id", "title", "difficulty", "description", "cooking_time"]
    if select:
        selected_fields = [s.strip() for s in select.split(",") if s.strip()]
        basic_fields = [f for f in selected_fields if f in basic_fields]

    options = []
    if "cuisine" in includes:
        options.append(selectinload(Recipe.cuisine))
    if "allergens" in includes:
        options.append(selectinload(Recipe.allergens))
    if "ingredients" in includes:
        options.append(selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient))

    stmt = (
        sql_select(Recipe)
        .join(Recipe.recipe_ingredients)
        .where(RecipeIngredient.ingredient_id == ingredient_id)
        .options(*options)
        .order_by(Recipe.id)
    )
    
    result = await session.scalars(stmt)
    recipes_list = result.all()
    
    response = []
    for recipe in recipes_list:
        data = {field: getattr(recipe, field) for field in basic_fields}
        
        if "cuisine" in includes:
            data["cuisine"] = (
                {"id": recipe.cuisine.id, "name": recipe.cuisine.name}
                if recipe.cuisine
                else None
            )
        
        if "allergens" in includes:
            data["allergens"] = [
                {"id": allergen.id, "name": allergen.name}
                for allergen in recipe.allergens
            ]
        
        if "ingredients" in includes:
            ingredients_data = []
            for ri in recipe.recipe_ingredients:
                if ri.ingredient:
                    measurement_str = ri.measurement.label if hasattr(ri.measurement, 'label') else str(ri.measurement)
                    ingredients_data.append({
                        "ingredient": {
                            "id": ri.ingredient.id,
                            "name": ri.ingredient.name
                        },
                        "quantity": ri.quantity,
                        "measurement": measurement_str
                    })
            data["ingredients"] = ingredients_data
        
        response.append(data)
    
    return response

@router.get("", response_model=list[IngredientRead])
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    stmt = sql_select(Ingredient).order_by(Ingredient.id)
    ingredients = await session.scalars(stmt)
    return ingredients.all()

@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
async def store(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ingredient_create: IngredientRead
):
    existing = await session.scalar(
        sql_select(Ingredient).where(Ingredient.name == ingredient_create.name)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with name '{ingredient_create.name}' already exists"
        )

    ingredient = Ingredient(name=ingredient_create.name)
    session.add(ingredient)
    await session.commit()
    return ingredient

@router.get("/{id}", response_model=IngredientRead)
async def show(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {id} not found"
        )
    return ingredient

@router.put("/{id}", response_model=IngredientRead)
async def update(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
    ingredient_update: IngredientRead
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {id} not found"
        )
    
    existing = await session.scalar(
        sql_select(Ingredient).where(Ingredient.name == ingredient_update.name, Ingredient.id != id)
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ingredient with name '{ingredient_update.name}' already exists"
        )
    
    ingredient.name = ingredient_update.name
    await session.commit()
    return ingredient

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
):
    ingredient = await session.get(Ingredient, id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {id} not found"
        )
    await session.delete(ingredient)
    await session.commit()