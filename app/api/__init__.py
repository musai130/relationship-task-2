from fastapi import APIRouter,Depends
from fastapi.security import HTTPBearer
from config import settings

from .test import router as test_router
from .posts import router as posts_router
from .recipes import router as recipe_router
from .ingredient import router as ingredient
from .cuisine import router as cuisine
from .allergen import router as allergen
from .auth import router as auth_router
from .videos import router as videos_router
http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=settings.url.prefix,
    dependencies=[Depends(http_bearer)],
)
router.include_router(test_router)
router.include_router(posts_router)
router.include_router(recipe_router)
router.include_router(ingredient)
router.include_router(cuisine)
router.include_router(allergen)
router.include_router(auth_router)
router.include_router(videos_router)