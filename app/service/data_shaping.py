"""
Чистые функции для обработки параметров include и select (data shaping).
Эти функции не зависят от SQLAlchemy, FastAPI или базы данных.
"""

from typing import List, Dict, Any, Optional, Set


# Уровень 0: Чистые функции для парсинга параметров

def parse_include_param(include: Optional[str]) -> Set[str]:
    """
    Парсит параметр include в множество строк.
    """
    if not include:
        return set()
    
    includes = [i.strip() for i in include.split(",") if i.strip()]
    return set(includes)


def parse_select_param(select: Optional[str], available_fields: List[str]) -> List[str]:
    """
    Парсит параметр select и фильтрует только допустимые поля.
    """
    if not select:
        return available_fields.copy()
    
    selected_fields = [s.strip() for s in select.split(",") if s.strip()]

    return [f for f in selected_fields if f in available_fields]


# Уровень 1: Функции для формирования данных связанных сущностей

def format_cuisine_data(cuisine: Any) -> Optional[Dict[str, Any]]:
    """
    Форматирует данные кухни в словарь.
    """
    if not cuisine:
        return None
    return {"id": cuisine.id, "name": cuisine.name}


def format_allergen_data(allergen: Any) -> Dict[str, Any]:
    """
    Форматирует данные аллергена в словарь.
    """
    return {"id": allergen.id, "name": allergen.name}


def format_allergens_data(allergens: List[Any]) -> List[Dict[str, Any]]:
    """
    Форматирует список аллергенов в список словарей.
    """
    return [format_allergen_data(allergen) for allergen in allergens]


def format_recipe_ingredient_data(recipe_ingredient: Any) -> Optional[Dict[str, Any]]:
    """
    Форматирует данные ингредиента рецепта в словарь.
    """
    if not recipe_ingredient or not recipe_ingredient.ingredient:
        return None
    
    measurement_str = (
        recipe_ingredient.measurement.label 
        if hasattr(recipe_ingredient.measurement, 'label') 
        else str(recipe_ingredient.measurement)
    )
    
    return {
        "ingredient": {
            "id": recipe_ingredient.ingredient.id,
            "name": recipe_ingredient.ingredient.name
        },
        "quantity": recipe_ingredient.quantity,
        "measurement": measurement_str
    }


def format_recipe_ingredients_data(recipe_ingredients: List[Any]) -> List[Dict[str, Any]]:
    """
    Форматирует список ингредиентов рецепта в список словарей.
    """
    formatted = [format_recipe_ingredient_data(ri) for ri in recipe_ingredients]
    return [item for item in formatted if item is not None]


# Уровень 2: Основная функция для формирования данных рецепта

def format_recipe_data(
    recipe: Any,
    selected_fields: List[str],
    includes: Set[str]
) -> Dict[str, Any]:
    """
    Форматирует данные рецепта с учетом выбранных полей и связанных данных.
    """

    data = {field: getattr(recipe, field) for field in selected_fields}
    

    if "cuisine" in includes:
        data["cuisine"] = format_cuisine_data(recipe.cuisine if hasattr(recipe, 'cuisine') else None)
    
    if "allergens" in includes:
        allergens = getattr(recipe, 'allergens', [])
        data["allergens"] = format_allergens_data(allergens)
    
    if "ingredients" in includes:
        recipe_ingredients = getattr(recipe, 'recipe_ingredients', [])
        data["ingredients"] = format_recipe_ingredients_data(recipe_ingredients)
    
    return data


def format_recipes_data(
    recipes: List[Any],
    selected_fields: List[str],
    includes: Set[str]
) -> List[Dict[str, Any]]:
    """
    Форматирует список рецептов с учетом выбранных полей и связанных данных.
    """
    return [format_recipe_data(recipe, selected_fields, includes) for recipe in recipes]

