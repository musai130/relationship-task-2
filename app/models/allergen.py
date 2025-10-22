from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List
from .base import Base


if TYPE_CHECKING:
    from .recipe import Recipe
    
from .recipe import recipe_allergens

class Allergen(Base):
    __tablename__ = 'allergen'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    recipes: Mapped[List["Recipe"]] = relationship(
        "Recipe", 
        secondary=recipe_allergens, 
        back_populates="allergens"
    )
    
    def __repr__(self):
        return f"<Allergen(id={self.id}, name='{self.name}')>"