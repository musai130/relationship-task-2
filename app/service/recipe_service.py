from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from models import (
    Recipe,
    RecipeIngredient,
    SessionDep,
    Cuisine,
    Allergen,
    Ingredient,
)
from models.recipe_ingredients import MeasurementEnum
from schemas import RecipeCreate
from repositories.recipe_repository import RecipeRepository
from repositories.cuisine_repository import CuisineRepository
from repositories.allergen_repository import AllergenRepository
from repositories.ingredient_repository import IngredientRepository
from repositories.recipe_ingredient_repository import RecipeIngredientRepository
from exceptions import (
    CuisineNotFoundException,
    AllergenNotFoundException,
    IngredientNotFoundException,
    RecipeNotFoundException,
    RecipeAccessForbiddenException,
)
from models.users import User


def parse_measurement(measurement_value: str | int) -> MeasurementEnum:
    if isinstance(measurement_value, MeasurementEnum):
        return measurement_value
    
    if isinstance(measurement_value, int):
        try:
            return MeasurementEnum(measurement_value)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid measurement value: '{measurement_value}'. Allowed values: 1 (grams), 2 (pieces), 3 (milliliters)"
            )
    
    measurement_str = str(measurement_value)
    measurement_lower = measurement_str.lower().strip()
    
    if measurement_lower in ['g', 'г', 'grams', 'gram', 'граммы', 'грамм', '1']:
        return MeasurementEnum.GRAMS

    if measurement_lower in ['шт', 'pieces', 'piece', 'pcs', 'pc', 'штуки', 'штука', '2']:
        return MeasurementEnum.PIECES
    
    if measurement_lower in ['ml', 'мл', 'milliliters', 'milliliter', 'миллилитры', 'миллилитр', '3']:
        return MeasurementEnum.MILLILITERS
    
    try:
        return MeasurementEnum[measurement_str.upper()]
    except (KeyError, AttributeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid measurement value: '{measurement_str}'. Allowed values: 'g'/'г' (grams), 'шт'/'pieces' (pieces), 'ml'/'мл' (milliliters)"
        )


class RecipeService:
    def __init__(
        self,
        session: SessionDep,
        recipe_repository: Annotated[
            RecipeRepository,
            Depends(RecipeRepository),
        ],
        cuisine_repository: Annotated[
            CuisineRepository,
            Depends(CuisineRepository),
        ],
        allergen_repository: Annotated[
            AllergenRepository,
            Depends(AllergenRepository),
        ],
        ingredient_repository: Annotated[
            IngredientRepository,
            Depends(IngredientRepository),
        ],
        recipe_ingredient_repository: Annotated[
            RecipeIngredientRepository,
            Depends(RecipeIngredientRepository),
        ],
    ):
        self.session = session
        self.recipe_repository = recipe_repository
        self.cuisine_repository = cuisine_repository
        self.allergen_repository = allergen_repository
        self.ingredient_repository = ingredient_repository
        self.recipe_ingredient_repository = recipe_ingredient_repository

    async def create(self, recipe_create: RecipeCreate, user: User) -> Recipe:
        cuisine = None
        if recipe_create.cuisine_id:
            cuisine = await self.cuisine_repository.get_one(recipe_create.cuisine_id)
            if not cuisine:
                raise CuisineNotFoundException()

        allergens = []
        if recipe_create.allergen_ids:
            allergens = await self.allergen_repository.get_many(recipe_create.allergen_ids)
            
            if len(allergens) != len(recipe_create.allergen_ids):
                found_ids = {a.id for a in allergens}
                missing_ids = set(recipe_create.allergen_ids) - found_ids
                raise AllergenNotFoundException(missing_ids=list(missing_ids))

        ingredient_ids = [ing.ingredient_id for ing in recipe_create.ingredients]
        if ingredient_ids:
            existing_ingredients = await self.ingredient_repository.get_many(ingredient_ids)
            
            if len(existing_ingredients) != len(ingredient_ids):
                found_ids = {i.id for i in existing_ingredients}
                missing_ids = set(ingredient_ids) - found_ids
                raise IngredientNotFoundException(missing_ids=list(missing_ids))

        recipe = Recipe(
            title=recipe_create.title,
            description=recipe_create.description,
            cooking_time=recipe_create.cooking_time,
            difficulty=recipe_create.difficulty,
            cuisine_id=recipe_create.cuisine_id,
            allergens=allergens,
            author_id=user.id
        )

        self.recipe_repository.save(recipe)
        await self.session.flush()

        for ing_data in recipe_create.ingredients:
            measurement_enum = parse_measurement(ing_data.measurement)
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ing_data.ingredient_id,
                quantity=ing_data.quantity,
                measurement=measurement_enum
            )
            self.recipe_ingredient_repository.save(recipe_ingredient)

        await self.session.commit()
        
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
        recipe_with_relations = await self.session.scalar(stmt)
        
        return recipe_with_relations

    async def update(self, recipe_id: int, recipe_in: RecipeCreate, user: User) -> Recipe:
        recipe = await self.recipe_repository.get_one(recipe_id)
        
        if not recipe:
            raise RecipeNotFoundException()
        
        if recipe.author_id != user.id:
            raise RecipeAccessForbiddenException()
        
        recipe.title = recipe_in.title
        recipe.description = recipe_in.description
        recipe.cooking_time = recipe_in.cooking_time
        recipe.difficulty = recipe_in.difficulty
        
        if recipe_in.cuisine_id:
            cuisine = await self.cuisine_repository.get_one(recipe_in.cuisine_id)
            if not cuisine:
                raise CuisineNotFoundException()
            recipe.cuisine = cuisine
        else:
            recipe.cuisine = None
        
        allergens = []
        if recipe_in.allergen_ids:
            allergens = await self.allergen_repository.get_many(recipe_in.allergen_ids)
            
            if len(allergens) != len(recipe_in.allergen_ids):
                found_ids = {a.id for a in allergens}
                missing_ids = set(recipe_in.allergen_ids) - found_ids
                raise AllergenNotFoundException(missing_ids=list(missing_ids))
        recipe.allergens = allergens
        
        ingredient_ids = [ing.ingredient_id for ing in recipe_in.ingredients]
        if ingredient_ids:
            existing_ingredients = await self.ingredient_repository.get_many(ingredient_ids)
            
            if len(existing_ingredients) != len(ingredient_ids):
                found_ids = {i.id for i in existing_ingredients}
                missing_ids = set(ingredient_ids) - found_ids
                raise IngredientNotFoundException(missing_ids=list(missing_ids))

        old_ingredients = await self.recipe_ingredient_repository.get_by_recipe_id(recipe_id)
        for old_ingredient in old_ingredients:
            await self.recipe_ingredient_repository.delete(old_ingredient)
        
        for ing_data in recipe_in.ingredients:
            measurement_enum = parse_measurement(ing_data.measurement)
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ing_data.ingredient_id,
                quantity=ing_data.quantity,
                measurement=measurement_enum
            )
            self.recipe_ingredient_repository.save(recipe_ingredient)
        
        await self.session.commit()
        
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
        recipe_with_relations = await self.session.scalar(stmt)
        
        return recipe_with_relations

    async def delete(self, recipe_id: int, user: User) -> None:
        recipe = await self.recipe_repository.get_one(recipe_id)
        
        if not recipe:
            raise RecipeNotFoundException()
        
        if recipe.author_id != user.id:
            raise RecipeAccessForbiddenException()
        
        await self.recipe_repository.delete(recipe)
        await self.session.commit()

