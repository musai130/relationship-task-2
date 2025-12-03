from typing import Any


class AppException(Exception):

    status_code: int = 500
    code: str = "internal_error"
    message: str = "Внутренняя ошибка сервера"

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        extra: dict[str, Any] | None = None,
    ):
        if message:
            self.message = message
        if code:
            self.code = code
        self.extra = extra or {}

    def to_dict(self) -> dict[str, Any]:
        data = {
            "error": {
                "code": self.code,
                "message": self.message,
            }
        }
        if self.extra:
            data["error"]["extra"] = self.extra
        return data


class NotFoundException(AppException):
    status_code = 404
    code = "not_found"
    message = "Объект не найден"


class RecipeNotFoundException(NotFoundException):
    message = "Рецепт не найден"


class CuisineNotFoundException(NotFoundException):
    message = "Кухня не найдена"


class AllergenNotFoundException(NotFoundException):
    message = "Аллерген не найден"

    def __init__(self, missing_ids: list[int] | None = None):
        extra = {}
        if missing_ids:
            extra["missing_ids"] = missing_ids
        super().__init__(extra=extra if extra else None)


class IngredientNotFoundException(NotFoundException):
    message = "Ингредиент не найден"

    def __init__(self, missing_ids: list[int] | None = None):
        extra = {}
        if missing_ids:
            extra["missing_ids"] = missing_ids
        super().__init__(extra=extra if extra else None)


class ForbiddenException(AppException):
    status_code = 403
    code = "forbidden"
    message = "Доступ запрещен"


class RecipeAccessForbiddenException(ForbiddenException):
    message = "Вы не являетесь автором этого рецепта"

