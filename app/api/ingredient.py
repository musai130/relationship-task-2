from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from models.recipe import Recipe
from models.recipe_ingredients import RecipeIngredient
from schemas import AllergenRead, CuisineRead, IngredientCreate, IngredientRead, RecipeIngredientRead, RecipeRead
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models import db_helper, Ingredient
from config import settings

router = APIRouter(
    tags=["Ingredients"],
    prefix=settings.url.ingredient,
)

@router.get("", response_model=list[IngredientRead])
async def index(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
):
    stmt = select(Ingredient).order_by(Ingredient.id)
    ingredients = await session.scalars(stmt)
    return ingredients.all()

@router.post("", response_model=IngredientRead, status_code=status.HTTP_201_CREATED)
async def store(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    ingredient_create: IngredientCreate
):
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
    return ingredient

@router.put("/{id}", response_model=IngredientRead)
async def update(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
    ingredient_update: IngredientCreate
):
    ingredient = await session.get(Ingredient, id)
    ingredient.name = ingredient_update.name
    await session.commit()
    return ingredient

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def destroy(
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    id: int,
):
    ingredient = await session.get(Ingredient, id)
    await session.delete(ingredient)
    await session.commit()

@router.get("/{ingredient_id}/recipes", response_model=List[RecipeRead])
async def get_recipes_by_ingredient(
    session: Annotated[
        AsyncSession,
        Depends(db_helper.session_getter),
    ],
    ingredient_id: int,
):

    ingredient = await session.get(Ingredient, ingredient_id)
    if not ingredient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ingredient with id {ingredient_id} not found"
        )

    stmt = (
        select(Recipe)
        .join(Recipe.recipe_ingredients)
        .where(RecipeIngredient.ingredient_id == ingredient_id)
        .options(
            selectinload(Recipe.cuisine),
            selectinload(Recipe.allergens),
            selectinload(Recipe.recipe_ingredients).selectinload(RecipeIngredient.ingredient)
        )
        .order_by(Recipe.id)
    )
    
    recipes = await session.scalars(stmt)
    recipes_list = recipes.all()
    
    result = []
    for recipe in recipes_list:
       
        cuisine = None
        if recipe.cuisine:
            cuisine = CuisineRead(
                id=recipe.cuisine.id,
                name=recipe.cuisine.name
            )

        allergens = []
        for allergen in recipe.allergens:
            allergens.append(AllergenRead(
                id=allergen.id,
                name=allergen.name
            ))

        ingredients = []
        for ri in recipe.recipe_ingredients:
            if ri.ingredient is None:
                continue

            ingredient_read = IngredientRead(
                id=ri.ingredient.id,
                name=ri.ingredient.name
            )
            recipe_ingredient_read = RecipeIngredientRead(
                ingredient=ingredient_read,
                quantity=ri.quantity,
                measurement=ri.measurement
            )
            ingredients.append(recipe_ingredient_read)
        
        recipe_read = RecipeRead(
            id=recipe.id,
            title=recipe.title,
            description=recipe.description,
            cooking_time=recipe.cooking_time,
            difficulty=recipe.difficulty,
            cuisine=cuisine,
            allergens=allergens,
            ingredients=ingredients
        )
        
        result.append(recipe_read)
    
    return result