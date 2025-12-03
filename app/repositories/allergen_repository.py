from typing import List
from sqlalchemy import select
from models import Allergen, SessionDep


class AllergenRepository:
    def __init__(
        self,
        session: SessionDep,
    ):
        self.session = session

    async def get_many(self, ids: List[int]) -> List[Allergen]:
        stmt = select(Allergen).where(Allergen.id.in_(ids))
        result = await self.session.scalars(stmt)
        return result.all()

