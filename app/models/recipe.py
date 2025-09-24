
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional, TYPE_CHECKING

from .base import Base

if TYPE_CHECKING:
    from .cuisine import Cuisine
    from .allergen import Allergen
    from .recipe_ingredients import RecipeIngredient

recipe_allergens = Table(
    'recipe_allergens',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipe.id'), primary_key=True),
    Column('allergen_id', Integer, ForeignKey('allergen.id'), primary_key=True)
)

class Recipe(Base):
    __tablename__ = "recipe"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    cooking_time: Mapped[int] = mapped_column(Integer)
    difficulty: Mapped[int] = mapped_column(Integer, default=1)
    cuisine_id: Mapped[Optional[int]] = mapped_column(ForeignKey('cuisine.id'), nullable=True, index=True)
    
    cuisine: Mapped["Cuisine"] = relationship("Cuisine", back_populates="recipes")
    allergens: Mapped[List["Allergen"]] = relationship(
        "Allergen", 
        secondary=recipe_allergens, 
        back_populates="recipes"
    )
    recipe_ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        "RecipeIngredient", 
        back_populates="recipe",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"Recipe(id={self.id}, title={self.title})"