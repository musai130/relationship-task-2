from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship

from .base import Base

recipe_allergens = Table(
    'recipe_allergens',
    Base.metadata,
    Column('recipe_id', Integer, ForeignKey('recipe.id'), primary_key=True),
    Column('allergen_id', Integer, ForeignKey('allergen.id'), primary_key=True)
)

class recipe_allergens(Base):
    __tablename__ = "recipe_allergens"

    recipe_id : Mapped[int] = relationship(back_populates="parent")
    allergen_id: Mapped[int] = relationship(back_populates="parent")