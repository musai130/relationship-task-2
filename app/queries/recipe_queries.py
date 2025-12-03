from typing import Optional
from sqlalchemy import Select, select
from sqlalchemy.orm import selectinload
from models import Recipe, RecipeIngredient, SessionDep
from exceptions import RecipeNotFoundException
from fastapi_filter.contrib.sqlalchemy import Filter
from fastapi_filter import FilterDepends, with_prefix


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


class RecipeQueries:
    def __init__(
        self,
        session: SessionDep,
    ):
        self.session = session

    def get_recipes_query(self) -> Select[tuple[Recipe]]:
        return (
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

    def filtered_query(self, filter: RecipeFilter) -> Select[tuple[Recipe]]:
        query = self.get_recipes_query()
        query = filter.filter(query)
        query = filter.sort(query)
        return query

    async def get_by_id(self, recipe_id: int) -> Recipe:
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
        recipe = await self.session.scalar(stmt)
        
        if not recipe:
            raise RecipeNotFoundException()
        
        return recipe

