from models import Cuisine, SessionDep


class CuisineRepository:
    def __init__(
        self,
        session: SessionDep,
    ):
        self.session = session

    async def get_one(self, id: int) -> Cuisine | None:
        return await self.session.get(Cuisine, id)

