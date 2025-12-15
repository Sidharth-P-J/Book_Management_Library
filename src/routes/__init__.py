"""Routes module initialization."""

from src.routes.auth_routes import router as auth_router
from src.routes.book_routes import router as book_router
from src.routes.review_routes import router as review_router
from src.routes.recommendation_routes import router as recommendation_router

__all__ = [
    "auth_router",
    "book_router",
    "review_router",
    "recommendation_router",
]
