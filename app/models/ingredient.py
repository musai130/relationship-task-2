from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List
from .base import Base

if TYPE_CHECKING:
    from .recipe_ingredients import RecipeIngredient

class Ingredient(Base):
    __tablename__ = 'ingredient'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    recipe_ingredients: Mapped[List["RecipeIngredient"]] = relationship(
        "RecipeIngredient", 
        back_populates="ingredient"
    )
    
    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}')>"