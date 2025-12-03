from typing import List
from sqlalchemy import select
from models import RecipeIngredient, SessionDep


class RecipeIngredientRepository:
    def __init__(
        self,
        session: SessionDep,
    ):
        self.session = session

    async def get_by_recipe_id(self, recipe_id: int) -> List[RecipeIngredient]:
        stmt = select(RecipeIngredient).where(RecipeIngredient.recipe_id == recipe_id)
        result = await self.session.scalars(stmt)
        return result.all()

    def save(self, recipe_ingredient: RecipeIngredient) -> None:
        self.session.add(recipe_ingredient)

    async def delete(self, recipe_ingredient: RecipeIngredient) -> None:
        await self.session.delete(recipe_ingredient)

