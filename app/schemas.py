from typing import List, Optional
from pydantic import BaseModel, Field

# === Cuisine ===
class CuisineBase(BaseModel):
    name: str = Field(..., example="Italian")

class CuisineRead(CuisineBase):
    id: int

# === Allergen ===
class AllergenBase(BaseModel):
    name: str = Field(..., example="Gluten")

class AllergenRead(AllergenBase):
    id: int

# === Ingredient ===
class IngredientBase(BaseModel):
    name: str = Field(..., example="Tomato")

class IngredientRead(IngredientBase):
    id: int

# === RecipeIngredient ===
class RecipeIngredientBase(BaseModel):
    ingredient_id: int = Field(..., example=1, description="ID ингредиента")
    quantity: float = Field(..., example=2.5, description="Количество")
    measurement: str = Field(..., example="g", description="Единица измерения (гр, мл и т.п.)")

class RecipeIngredientRead(BaseModel):
    ingredient: IngredientRead
    quantity: float
    measurement: str

# === Recipe ===
class RecipeCreate(BaseModel):
    title: str = Field(..., example="Spaghetti Bolognese")
    description: str = Field(..., example="A classic Italian pasta dish with meat sauce.")
    cooking_time: int = Field(..., example=45, description="Время приготовления в минутах")
    difficulty: int = Field(..., example=3, description="Сложность от 1 до 5")
    cuisine_id: Optional[int] = Field(None, example=1, description="ID кухни")
    allergens: Optional[List[int]] = Field(default_factory=list, description="ID аллергенов")
    ingredients: List[RecipeIngredientBase] = Field(..., description="Список ингредиентов с количеством")

class RecipeRead(BaseModel):
    id: int
    title: str
    description: str
    cooking_time: int
    difficulty: int
    cuisine: Optional[CuisineRead]
    allergens: List[AllergenRead]
    ingredients: List[RecipeIngredientRead]

    class Config:
        orm_mode = True
