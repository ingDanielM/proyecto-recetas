from app.routers.ingredients import router as ingredients_router
from app.routers.recipes import router as recipes_router
from app.routers.auth import router as auth_router
from app.routers.frontend import router as frontend_router

__all__ = ["ingredients_router", "recipes_router", "auth_router", "frontend_router"]