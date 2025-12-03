"""
Unit-тесты для логики include и data shaping.
Тесты не зависят от базы данных, SQL или FastAPI - только чистая логика.
"""

import sys
from pathlib import Path

# Добавляем путь к app в PYTHONPATH для импортов
app_path = Path(__file__).parent.parent.parent
if str(app_path) not in sys.path:
    sys.path.insert(0, str(app_path))

import pytest
from service.data_shaping import (
    parse_include_param,
    parse_select_param,
    format_cuisine_data,
    format_allergen_data,
    format_allergens_data,
    format_recipe_ingredient_data,
    format_recipe_ingredients_data,
    format_recipe_data,
    format_recipes_data,
)



def test_parse_include_param_single_value():
    """Тест парсинга одного значения include."""
    result = parse_include_param("cuisine")
    assert result == {"cuisine"}


def test_parse_include_param_multiple_values():
    """Тест парсинга нескольких значений include через запятую."""
    result = parse_include_param("cuisine,ingredients,allergens")
    assert result == {"cuisine", "ingredients", "allergens"}


def test_parse_include_param_with_spaces():
    """Тест парсинга include с пробелами."""
    result = parse_include_param(" cuisine , ingredients , allergens ")
    assert result == {"cuisine", "ingredients", "allergens"}


def test_parse_include_param_none():
    """Тест парсинга None значения."""
    result = parse_include_param(None)
    assert result == set()


def test_parse_include_param_empty_string():
    """Тест парсинга пустой строки."""
    result = parse_include_param("")
    assert result == set()


def test_parse_include_param_empty_with_commas():
    """Тест парсинга строки только с запятыми и пробелами."""
    result = parse_include_param(" , , , ")
    assert result == set()


def test_parse_include_param_duplicates():
    """Тест парсинга дублирующихся значений (должны быть удалены через set)."""
    result = parse_include_param("cuisine,cuisine,ingredients")
    assert result == {"cuisine", "ingredients"}


@pytest.mark.parametrize(
    "include_input,expected",
    [
        ("cuisine", {"cuisine"}),
        ("ingredients", {"ingredients"}),
        ("allergens", {"allergens"}),
        ("cuisine,ingredients", {"cuisine", "ingredients"}),
        ("cuisine,allergens", {"cuisine", "allergens"}),
        ("ingredients,allergens", {"ingredients", "allergens"}),
        ("cuisine,ingredients,allergens", {"cuisine", "ingredients", "allergens"}),
    ],
)
def test_parse_include_param_parametrized(include_input, expected):
    """Параметризованный тест для различных комбинаций include."""
    result = parse_include_param(include_input)
    assert result == expected



def test_parse_select_param_none_returns_all_fields():
    """Тест: если select=None, возвращаются все доступные поля."""
    available_fields = ["id", "title", "difficulty", "description", "cooking_time"]
    result = parse_select_param(None, available_fields)
    assert result == available_fields


def test_parse_select_param_empty_string_returns_all_fields():
    """Тест: если select="", возвращаются все доступные поля."""
    available_fields = ["id", "title", "difficulty", "description", "cooking_time"]
    result = parse_select_param("", available_fields)
    assert result == available_fields


def test_parse_select_param_single_field():
    """Тест парсинга одного поля."""
    available_fields = ["id", "title", "difficulty", "description", "cooking_time"]
    result = parse_select_param("id", available_fields)
    assert result == ["id"]


def test_parse_select_param_multiple_fields():
    """Тест парсинга нескольких полей."""
    available_fields = ["id", "title", "difficulty", "description", "cooking_time"]
    result = parse_select_param("id,title", available_fields)
    assert result == ["id", "title"]


def test_parse_select_param_with_spaces():
    """Тест парсинга select с пробелами."""
    available_fields = ["id", "title", "difficulty", "description", "cooking_time"]
    result = parse_select_param(" id , title , difficulty ", available_fields)
    assert result == ["id", "title", "difficulty"]


def test_parse_select_param_filters_invalid_fields():
    """Тест: недопустимые поля должны быть отфильтрованы."""
    available_fields = ["id", "title", "difficulty", "description", "cooking_time"]
    result = parse_select_param("id,invalid_field,title,another_invalid", available_fields)
    assert result == ["id", "title"]


def test_parse_select_param_only_invalid_fields():
    """Тест: если все поля недопустимы, возвращается пустой список."""
    available_fields = ["id", "title", "difficulty", "description", "cooking_time"]
    result = parse_select_param("invalid1,invalid2", available_fields)
    assert result == []


def test_parse_select_param_preserves_order():
    """Тест: порядок полей должен сохраняться."""
    available_fields = ["id", "title", "difficulty", "description", "cooking_time"]
    result = parse_select_param("difficulty,id,title", available_fields)
    assert result == ["difficulty", "id", "title"]


@pytest.mark.parametrize(
    "select_input,available_fields,expected",
    [
        ("id", ["id", "title"], ["id"]),
        ("id,title", ["id", "title"], ["id", "title"]),
        ("title,id", ["id", "title"], ["title", "id"]),
        ("id,invalid", ["id", "title"], ["id"]),
        ("invalid1,invalid2", ["id", "title"], []),
    ],
)
def test_parse_select_param_parametrized(select_input, available_fields, expected):
    """Параметризованный тест для различных комбинаций select."""
    result = parse_select_param(select_input, available_fields)
    assert result == expected


def test_format_cuisine_data_with_cuisine():
    """Тест форматирования данных кухни."""
    class MockCuisine:
        def __init__(self):
            self.id = 1
            self.name = "Italian"
    
    cuisine = MockCuisine()
    result = format_cuisine_data(cuisine)
    assert result == {"id": 1, "name": "Italian"}


def test_format_cuisine_data_none():
    """Тест форматирования None кухни."""
    result = format_cuisine_data(None)
    assert result is None



def test_format_allergen_data():
    """Тест форматирования данных аллергена."""
    class MockAllergen:
        def __init__(self):
            self.id = 1
            self.name = "Gluten"
    
    allergen = MockAllergen()
    result = format_allergen_data(allergen)
    assert result == {"id": 1, "name": "Gluten"}


def test_format_allergens_data_multiple():
    """Тест форматирования списка аллергенов."""
    class MockAllergen:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    allergens = [MockAllergen(1, "Gluten"), MockAllergen(2, "Dairy")]
    result = format_allergens_data(allergens)
    assert result == [
        {"id": 1, "name": "Gluten"},
        {"id": 2, "name": "Dairy"}
    ]


def test_format_allergens_data_empty_list():
    """Тест форматирования пустого списка аллергенов."""
    result = format_allergens_data([])
    assert result == []



def test_format_recipe_ingredient_data():
    """Тест форматирования данных ингредиента рецепта."""
    class MockIngredient:
        def __init__(self):
            self.id = 1
            self.name = "Flour"
    
    class MockMeasurement:
        label = "г"
    
    class MockRI:
        def __init__(self):
            self.ingredient = MockIngredient()
            self.quantity = 500.0
            self.measurement = MockMeasurement()
    
    ri = MockRI()
    result = format_recipe_ingredient_data(ri)
    assert result == {
        "ingredient": {"id": 1, "name": "Flour"},
        "quantity": 500.0,
        "measurement": "г"
    }


def test_format_recipe_ingredient_data_no_ingredient():
    """Тест форматирования RecipeIngredient без ingredient."""
    class MockRI:
        def __init__(self):
            self.ingredient = None
            self.quantity = 500.0
            self.measurement = "г"
    
    ri = MockRI()
    result = format_recipe_ingredient_data(ri)
    assert result is None


def test_format_recipe_ingredient_data_measurement_without_label():
    """Тест форматирования с measurement без атрибута label."""
    class MockIngredient:
        def __init__(self):
            self.id = 1
            self.name = "Sugar"
    
    class MockRI:
        def __init__(self):
            self.ingredient = MockIngredient()
            self.quantity = 200.0
            self.measurement = "grams"
    
    ri = MockRI()
    result = format_recipe_ingredient_data(ri)
    assert result == {
        "ingredient": {"id": 1, "name": "Sugar"},
        "quantity": 200.0,
        "measurement": "grams"
    }


def test_format_recipe_ingredients_data_multiple():
    """Тест форматирования списка ингредиентов рецепта."""
    class MockIngredient:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockMeasurement:
        def __init__(self, label):
            self.label = label
    
    class MockRI:
        def __init__(self, ingredient, quantity, measurement_label):
            self.ingredient = ingredient
            self.quantity = quantity
            self.measurement = MockMeasurement(measurement_label)
    
    ingredients = [
        MockIngredient(1, "Flour"),
        MockIngredient(2, "Sugar")
    ]
    ris = [
        MockRI(ingredients[0], 500.0, "г"),
        MockRI(ingredients[1], 200.0, "г")
    ]
    
    result = format_recipe_ingredients_data(ris)
    assert result == [
        {"ingredient": {"id": 1, "name": "Flour"}, "quantity": 500.0, "measurement": "г"},
        {"ingredient": {"id": 2, "name": "Sugar"}, "quantity": 200.0, "measurement": "г"}
    ]


def test_format_recipe_ingredients_data_filters_none():
    """Тест: None значения должны быть отфильтрованы."""
    class MockIngredient:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockMeasurement:
        label = "г"
    
    class MockRI:
        def __init__(self, ingredient, quantity):
            self.ingredient = ingredient
            self.quantity = quantity
            self.measurement = MockMeasurement()
    
    ris = [
        MockRI(MockIngredient(1, "Flour"), 500.0),
        MockRI(None, 200.0),  # Этот должен быть отфильтрован
        MockRI(MockIngredient(2, "Sugar"), 100.0)
    ]
    
    result = format_recipe_ingredients_data(ris)
    assert len(result) == 2
    assert result[0]["ingredient"]["name"] == "Flour"
    assert result[1]["ingredient"]["name"] == "Sugar"


def test_format_recipe_data_basic_fields_only():
    """Тест форматирования рецепта только с базовыми полями."""
    class MockRecipe:
        def __init__(self):
            self.id = 1
            self.title = "Pasta"
            self.difficulty = 2
            self.description = "Delicious pasta"
            self.cooking_time = 30
    
    recipe = MockRecipe()
    selected_fields = ["id", "title", "difficulty"]
    includes = set()
    
    result = format_recipe_data(recipe, selected_fields, includes)
    assert result == {
        "id": 1,
        "title": "Pasta",
        "difficulty": 2
    }


def test_format_recipe_data_with_cuisine():
    """Тест форматирования рецепта с включенной кухней."""
    class MockCuisine:
        def __init__(self):
            self.id = 1
            self.name = "Italian"
    
    class MockRecipe:
        def __init__(self):
            self.id = 1
            self.title = "Pasta"
            self.difficulty = 2
            self.description = "Delicious pasta"
            self.cooking_time = 30
            self.cuisine = MockCuisine()
    
    recipe = MockRecipe()
    selected_fields = ["id", "title"]
    includes = {"cuisine"}
    
    result = format_recipe_data(recipe, selected_fields, includes)
    assert result == {
        "id": 1,
        "title": "Pasta",
        "cuisine": {"id": 1, "name": "Italian"}
    }


def test_format_recipe_data_with_cuisine_none():
    """Тест форматирования рецепта с cuisine=None."""
    class MockRecipe:
        def __init__(self):
            self.id = 1
            self.title = "Pasta"
            self.difficulty = 2
            self.description = "Delicious pasta"
            self.cooking_time = 30
            self.cuisine = None
    
    recipe = MockRecipe()
    selected_fields = ["id", "title"]
    includes = {"cuisine"}
    
    result = format_recipe_data(recipe, selected_fields, includes)
    assert result == {
        "id": 1,
        "title": "Pasta",
        "cuisine": None
    }


def test_format_recipe_data_with_allergens():
    """Тест форматирования рецепта с включенными аллергенами."""
    class MockAllergen:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockRecipe:
        def __init__(self):
            self.id = 1
            self.title = "Pasta"
            self.difficulty = 2
            self.description = "Delicious pasta"
            self.cooking_time = 30
            self.allergens = [MockAllergen(1, "Gluten"), MockAllergen(2, "Dairy")]
    
    recipe = MockRecipe()
    selected_fields = ["id", "title"]
    includes = {"allergens"}
    
    result = format_recipe_data(recipe, selected_fields, includes)
    assert result == {
        "id": 1,
        "title": "Pasta",
        "allergens": [
            {"id": 1, "name": "Gluten"},
            {"id": 2, "name": "Dairy"}
        ]
    }


def test_format_recipe_data_with_ingredients():
    """Тест форматирования рецепта с включенными ингредиентами."""
    class MockIngredient:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockMeasurement:
        def __init__(self, label):
            self.label = label
    
    class MockRI:
        def __init__(self, ingredient, quantity, measurement_label):
            self.ingredient = ingredient
            self.quantity = quantity
            self.measurement = MockMeasurement(measurement_label)
    
    class MockRecipe:
        def __init__(self):
            self.id = 1
            self.title = "Pasta"
            self.difficulty = 2
            self.description = "Delicious pasta"
            self.cooking_time = 30
            self.recipe_ingredients = [
                MockRI(MockIngredient(1, "Flour"), 500.0, "г"),
                MockRI(MockIngredient(2, "Eggs"), 2.0, "шт")
            ]
    
    recipe = MockRecipe()
    selected_fields = ["id", "title"]
    includes = {"ingredients"}
    
    result = format_recipe_data(recipe, selected_fields, includes)
    assert result == {
        "id": 1,
        "title": "Pasta",
        "ingredients": [
            {"ingredient": {"id": 1, "name": "Flour"}, "quantity": 500.0, "measurement": "г"},
            {"ingredient": {"id": 2, "name": "Eggs"}, "quantity": 2.0, "measurement": "шт"}
        ]
    }


def test_format_recipe_data_all_includes():
    """Тест форматирования рецепта со всеми включенными связанными данными."""
    class MockCuisine:
        def __init__(self):
            self.id = 1
            self.name = "Italian"
    
    class MockAllergen:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockIngredient:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockMeasurement:
        def __init__(self, label):
            self.label = label
    
    class MockRI:
        def __init__(self, ingredient, quantity, measurement_label):
            self.ingredient = ingredient
            self.quantity = quantity
            self.measurement = MockMeasurement(measurement_label)
    
    class MockRecipe:
        def __init__(self):
            self.id = 1
            self.title = "Pasta"
            self.difficulty = 2
            self.description = "Delicious pasta"
            self.cooking_time = 30
            self.cuisine = MockCuisine()
            self.allergens = [MockAllergen(1, "Gluten")]
            self.recipe_ingredients = [
                MockRI(MockIngredient(1, "Flour"), 500.0, "г")
            ]
    
    recipe = MockRecipe()
    selected_fields = ["id", "title", "difficulty"]
    includes = {"cuisine", "allergens", "ingredients"}
    
    result = format_recipe_data(recipe, selected_fields, includes)
    assert result == {
        "id": 1,
        "title": "Pasta",
        "difficulty": 2,
        "cuisine": {"id": 1, "name": "Italian"},
        "allergens": [{"id": 1, "name": "Gluten"}],
        "ingredients": [
            {"ingredient": {"id": 1, "name": "Flour"}, "quantity": 500.0, "measurement": "г"}
        ]
    }


def test_format_recipe_data_no_attributes_for_includes():
    """Тест: если у рецепта нет атрибутов для include, они не должны вызывать ошибку."""
    class MockRecipe:
        def __init__(self):
            self.id = 1
            self.title = "Pasta"
            self.difficulty = 2
            self.description = "Delicious pasta"
            self.cooking_time = 30
    
    recipe = MockRecipe()
    selected_fields = ["id", "title"]
    includes = {"cuisine", "allergens", "ingredients"}
    
    result = format_recipe_data(recipe, selected_fields, includes)
    assert result == {
        "id": 1,
        "title": "Pasta",
        "cuisine": None,
        "allergens": [],
        "ingredients": []
    }


def test_format_recipes_data_multiple_recipes():
    """Тест форматирования списка рецептов."""
    class MockRecipe:
        def __init__(self, id, title):
            self.id = id
            self.title = title
            self.difficulty = 2
            self.description = "Description"
            self.cooking_time = 30
    
    recipes = [MockRecipe(1, "Pasta"), MockRecipe(2, "Pizza")]
    selected_fields = ["id", "title"]
    includes = set()
    
    result = format_recipes_data(recipes, selected_fields, includes)
    assert result == [
        {"id": 1, "title": "Pasta"},
        {"id": 2, "title": "Pizza"}
    ]


def test_format_recipes_data_empty_list():
    """Тест форматирования пустого списка рецептов."""
    result = format_recipes_data([], ["id", "title"], set())
    assert result == []


def test_format_recipes_data_with_includes():
    """Тест форматирования списка рецептов с включенными данными."""
    class MockCuisine:
        def __init__(self, id, name):
            self.id = id
            self.name = name
    
    class MockRecipe:
        def __init__(self, id, title, cuisine_id, cuisine_name):
            self.id = id
            self.title = title
            self.difficulty = 2
            self.description = "Description"
            self.cooking_time = 30
            self.cuisine = MockCuisine(cuisine_id, cuisine_name) if cuisine_id else None
    
    recipes = [
        MockRecipe(1, "Pasta", 1, "Italian"),
        MockRecipe(2, "Sushi", 2, "Japanese")
    ]
    selected_fields = ["id", "title"]
    includes = {"cuisine"}
    
    result = format_recipes_data(recipes, selected_fields, includes)
    assert result == [
        {"id": 1, "title": "Pasta", "cuisine": {"id": 1, "name": "Italian"}},
        {"id": 2, "title": "Sushi", "cuisine": {"id": 2, "name": "Japanese"}}
    ]

