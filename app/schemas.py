from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, Field, validator, root_validator

class CuisineBase(BaseModel):
    name: str = Field(..., example="Italian")

class CuisineRead(CuisineBase):
    id: int
    
    class Config:
        orm_mode = True

class AllergenBase(BaseModel):
    name: str = Field(..., example="Gluten")

class AllergenRead(AllergenBase):
    id: int
    
    class Config:
        orm_mode = True

class IngredientBase(BaseModel):
    name: str = Field(..., example="Tomato")

class IngredientRead(IngredientBase):
    id: int

class RecipeIngredientBase(BaseModel):
    ingredient_id: int = Field(..., example=1, description="ID ингредиента")
    quantity: float = Field(..., example=2.5, description="Количество")
    measurement: str = Field(..., example="g", description="Единица измерения (гр, мл и т.п.)")

class RecipeCreate(BaseModel):
    title: str = Field(..., example="Spaghetti Bolognese")
    description: str = Field(..., example="A classic Italian pasta dish with meat sauce.")
    cooking_time: int = Field(..., example=45, description="Время приготовления в минутах")
    difficulty: int = Field(..., example=3, description="Сложность от 1 до 5")
    cuisine_id: Optional[int] = Field(None, example=1, description="ID кухни")
    allergens: Optional[List[int]] = Field(default_factory=list, description="ID аллергенов")
    ingredients: List[RecipeIngredientBase] = Field(..., description="Список ингредиентов с количеством")


class UserRead(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True

class AuthorRead(BaseModel):
    """Схема для автора рецепта"""
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode = True

class RecipeIngredientRead(BaseModel):
    """Схема для ингредиента в рецепте с id напрямую"""
    id: int
    quantity: float
    measurement: str
    
    @root_validator(pre=True)
    def extract_data(cls, values):
        """Извлекает данные из объекта RecipeIngredient"""
        if isinstance(values, dict):
            if 'id' in values and isinstance(values.get('id'), int) and 'quantity' in values and 'measurement' in values:
                return values
            if 'ingredient' in values:
                ing = values['ingredient']
                if ing and hasattr(ing, 'id'):
                    values['id'] = ing.id
                elif 'ingredient_id' in values:
                    values['id'] = values['ingredient_id']
                if 'ingredient' in values:
                    del values['ingredient']
            elif 'ingredient_id' in values:
                values['id'] = values['ingredient_id']
            return values
        
        if not isinstance(values, dict):
            data = {}
            ingredient_id = None
            if hasattr(values, 'ingredient') and values.ingredient:
                ingredient_id = getattr(values.ingredient, 'id', None)
            if ingredient_id is None and hasattr(values, 'ingredient_id'):
                ingredient_id = values.ingredient_id
            if ingredient_id is None:
                raise ValueError(f"RecipeIngredient object missing ingredient_id: {values}")
            data['id'] = ingredient_id
            
            if hasattr(values, 'quantity'):
                data['quantity'] = values.quantity
            else:
                data['quantity'] = 0.0
            
            if hasattr(values, 'measurement'):
                m = values.measurement
                data['measurement'] = m.label if hasattr(m, 'label') else (str(m) if m else "")
            else:
                data['measurement'] = ""
            
            return data
        
        return values
    
    @validator('measurement', pre=True)
    def convert_enum_to_str(cls, v):
        if hasattr(v, 'label'):
            return v.label
        return str(v) if v is not None else ""
    
    class Config:
        orm_mode = True

class RecipeRead(BaseModel):
    id: int
    title: str
    description: str
    cooking_time: int
    difficulty: int
    cuisine: Optional[CuisineRead] = None
    allergens: List[AllergenRead] = Field(default_factory=list)
    ingredients: List[RecipeIngredientRead] = Field(default_factory=list, alias="recipe_ingredients")
    author: AuthorRead
    class Config:
        orm_mode = True
        populate_by_name = True
