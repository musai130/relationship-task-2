from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, TypeDecorator, Integer, Enum as SQLEnum
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
    
    @classmethod
    def from_string(cls, value: str):
        if isinstance(value, cls):
            return value
        
        measurement_lower = str(value).lower().strip()
        
        if measurement_lower in ['g', 'г', 'grams', 'gram', 'граммы', 'грамм', '1']:
            return cls.GRAMS

        if measurement_lower in ['шт', 'pieces', 'piece', 'pcs', 'pc', 'штуки', 'штука', '2']:
            return cls.PIECES
        
        if measurement_lower in ['ml', 'мл', 'milliliters', 'milliliter', 'миллилитры', 'миллилитр', '3']:
            return cls.MILLILITERS
        
     
        try:
            return cls[value.upper()]
        except (KeyError, AttributeError):
            return cls.GRAMS


class MeasurementEnumType(TypeDecorator):
    impl = Integer
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(Integer())
    
    def process_bind_param(self, value, dialect):
        if isinstance(value, MeasurementEnum):
            return value.value
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return MeasurementEnum.from_string(value).value
        return value
    
    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, MeasurementEnum):
            return value
        if isinstance(value, int):
            try:
                return MeasurementEnum(value)
            except ValueError:
                return MeasurementEnum.GRAMS
        if isinstance(value, str):
            return MeasurementEnum.from_string(value)
        return value

class RecipeIngredient(Base):
    __tablename__ = 'recipe_ingredients'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey('recipe.id'), nullable=False, index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredient.id'), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(nullable=False)
    measurement: Mapped[MeasurementEnum] = mapped_column(
        MeasurementEnumType(),
        nullable=False
    )
    
    recipe: Mapped["Recipe"] = relationship("Recipe", back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship("Ingredient", back_populates="recipe_ingredients")
    
    def __repr__(self):
        return f"<RecipeIngredient(id={self.id}, recipe_id={self.recipe_id}, ingredient_id={self.ingredient_id})>"