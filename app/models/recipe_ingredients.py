from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .recipe import Recipe
from .ingredient import Ingredient

from enum import IntEnum


if TYPE_CHECKING:
    from .recipe import Recipe
    from .ingredient import Ingredient

class MeasurementEnum(IntEnum):
    GRAMS = 1
    PIECES = 2
    MILLILITERS = 3

    @property
    def label(self) -> str:
        return {
            MeasurementEnum.GRAMS: "г",
            MeasurementEnum.PIECES: "шт",
            MeasurementEnum.MILLILITERS: "мл",
        }[self]

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipe.id'), nullable=False, index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredient.id'), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(nullable=False)
    measurement: Mapped[MeasurementEnum] = mapped_column(nullable=False)
    
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="recipe_ingredients")
    
    def __repr__(self):
        return f"<RecipeIngredient(id={self.id}, recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id})>"