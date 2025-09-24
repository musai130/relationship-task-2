from typing import List, Optional
from pydantic import BaseModel

class CuisineRead(BaseModel):
    id: int
    name: str

class CuisineCreate(BaseModel):
    name: str

class AllergenRead(BaseModel):
    id: int
    name: str

class AllergenCreate(BaseModel):
    name: str

class IngredientRead(BaseModel):
    id: int
    name: str

class IngredientCreate(BaseModel):
    name: str

class RecipeIngredientCreate(BaseModel):
    ingredient_id: int
    quantity: float
    measurement: int

class RecipeCreate(BaseModel):
    title: str
    description: str
    cooking_time: int
    difficulty: int
    cuisine_id: Optional[int] = None
    allergen_ids: List[int] = []
    ingredients: List[RecipeIngredientCreate] = []

class RecipeIngredientRead(BaseModel):
    ingredient: IngredientRead
    quantity: float
    measurement: int
class RecipeRead(BaseModel):
    id: int
    title: str
    description: str
    cooking_time: int
    difficulty: int
    cuisine: Optional[CuisineRead] = None
    allergens: List[AllergenRead] = []
    ingredients: List[RecipeIngredientRead] = []
