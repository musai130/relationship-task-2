from models import Recipe, SessionDep


class RecipeRepository:
    def __init__(
        self,
        session: SessionDep,
    ):
        self.session = session

    def save(self, recipe: Recipe) -> None:
        self.session.add(recipe)

    async def delete(self, recipe: Recipe) -> None:
        await self.session.delete(recipe)

    async def get_one(self, id: int) -> Recipe | None:
        return await self.session.get(Recipe, id)

