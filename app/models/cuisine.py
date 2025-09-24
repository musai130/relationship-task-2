from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING, List
from .base import Base

if TYPE_CHECKING:
    from .recipe import Recipe
class Cuisine(Base):
    __tablename__ = 'cuisine'
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    
    
    recipes: Mapped[List["Recipe"]] = relationship("Recipe", back_populates="cuisine")
    
    def __repr__(self):
        return f"<Cuisine(id={self.id}, name='{self.name}')>"