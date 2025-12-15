"""Services module initialization."""

from src.services.user_service import UserService
from src.services.book_service import BookService
from src.services.review_service import ReviewService
from src.services.recommendation_service import RecommendationService

__all__ = [
    "UserService",
    "BookService",
    "ReviewService",
    "RecommendationService",
]
