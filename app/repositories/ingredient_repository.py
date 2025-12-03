from typing import List
from sqlalchemy import select
from models import Ingredient, SessionDep


class IngredientRepository:
    def __init__(
        self,
        session: SessionDep,
    ):
        self.session = session

    async def get_many(self, ids: List[int]) -> List[Ingredient]:
        stmt = select(Ingredient).where(Ingredient.id.in_(ids))
        result = await self.session.scalars(stmt)
        return result.all()

