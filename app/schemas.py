from typing import List, Optional, Union, Any, Dict
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional
from pydantic import BaseModel

class CuisineRead(BaseModel):
    id: int
    
    class Config:
        orm_mode = True
    name: str

class CuisineCreate(BaseModel):
    name: str

class AllergenRead(BaseModel):
    id: int
    
    class Config:
        orm_mode = True
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
    ingredients: List[RecipeIngredientCreate] =[]


class UserRead(BaseModel):
    id: int
    email: str

    class Config:
        orm_mode = True

class AuthorRead(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        orm_mode = True

class RecipeIngredientRead(BaseModel):
    id: int
    quantity: float
    measurement: str
    
    @root_validator(pre=True)
    def extract_data(cls, values):
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

class RecipeIngredientRead(BaseModel):
    ingredient: Optional[IngredientRead] = None
    quantity: float
    measurement: int
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
    allergens: List[AllergenRead] = []
    recipe_ingredients: List[RecipeIngredientRead] = [] 

class RecipeRead1(BaseModel):
    id: int
    title: str
    description: str
    cooking_time: int
    difficulty: int
    cuisine: Optional[CuisineRead] = None
    allergens: List[AllergenRead] = []
    ingredients: List[RecipeIngredientRead] = [] 
