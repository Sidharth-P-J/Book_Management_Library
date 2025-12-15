"""
Unit tests for the Review service.

This module tests review creation, retrieval,
updating, and deletion operations.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import ReviewService, UserService, BookService
from src.schemas import ReviewCreate, ReviewUpdate, UserCreate, BookCreate


@pytest.fixture
async def test_user(db_session: AsyncSession):
    """Create a test user."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )
    return await UserService.create_user(db_session, user_data)


@pytest.fixture
async def test_book(db_session: AsyncSession):
    """Create a test book."""
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        genre="Fiction",
    )
    return await BookService.create_book(db_session, book_data)


@pytest.mark.asyncio
async def test_create_review(db_session: AsyncSession, test_user, test_book):
    """Test creating a new review."""
    review_data = ReviewCreate(
        review_text="This is a great book!",
        rating=4.5,
    )

    review = await ReviewService.create_review(
        db_session, test_book.id, test_user.id, review_data
    )

    assert review.id is not None
    assert review.book_id == test_book.id
    assert review.user_id == test_user.id
    assert review.review_text == "This is a great book!"
    assert review.rating == 4.5


@pytest.mark.asyncio
async def test_get_review_by_id(db_session: AsyncSession, test_user, test_book):
    """Test retrieving a review by ID."""
    review_data = ReviewCreate(
        review_text="This is a great book!",
        rating=4.5,
    )

    created_review = await ReviewService.create_review(
        db_session, test_book.id, test_user.id, review_data
    )
    retrieved_review = await ReviewService.get_review_by_id(
        db_session, created_review.id
    )

    assert retrieved_review is not None
    assert retrieved_review.id == created_review.id
    assert retrieved_review.review_text == "This is a great book!"


@pytest.mark.asyncio
async def test_get_reviews_by_book(db_session: AsyncSession, test_user, test_book):
    """Test retrieving reviews for a book."""
    # Create multiple reviews
    for i in range(3):
        review_data = ReviewCreate(
            review_text=f"Review {i}",
            rating=3.0 + i,
        )
        await ReviewService.create_review(
            db_session, test_book.id, test_user.id, review_data
        )

    reviews, total = await ReviewService.get_reviews_by_book(
        db_session, test_book.id, skip=0, limit=10
    )

    assert len(reviews) == 3
    assert total == 3


@pytest.mark.asyncio
async def test_get_reviews_by_user(db_session: AsyncSession, test_user, test_book):
    """Test retrieving reviews by a user."""
    # Create multiple reviews by the same user
    for i in range(3):
        review_data = ReviewCreate(
            review_text=f"Review {i}",
            rating=3.0 + i,
        )
        await ReviewService.create_review(
            db_session, test_book.id, test_user.id, review_data
        )

    reviews, total = await ReviewService.get_reviews_by_user(
        db_session, test_user.id, skip=0, limit=10
    )

    assert len(reviews) == 3
    assert total == 3


@pytest.mark.asyncio
async def test_update_review(db_session: AsyncSession, test_user, test_book):
    """Test updating a review."""
    review_data = ReviewCreate(
        review_text="Original review",
        rating=3.0,
    )

    created_review = await ReviewService.create_review(
        db_session, test_book.id, test_user.id, review_data
    )

    update_data = ReviewUpdate(
        review_text="Updated review",
        rating=5.0,
    )

    updated_review = await ReviewService.update_review(
        db_session, created_review.id, update_data
    )

    assert updated_review is not None
    assert updated_review.review_text == "Updated review"
    assert updated_review.rating == 5.0


@pytest.mark.asyncio
async def test_delete_review(db_session: AsyncSession, test_user, test_book):
    """Test deleting a review."""
    review_data = ReviewCreate(
        review_text="Review to delete",
        rating=3.0,
    )

    created_review = await ReviewService.create_review(
        db_session, test_book.id, test_user.id, review_data
    )

    success = await ReviewService.delete_review(db_session, created_review.id)
    assert success is True

    deleted_review = await ReviewService.get_review_by_id(
        db_session, created_review.id
    )
    assert deleted_review is None


@pytest.mark.asyncio
async def test_get_book_rating_summary(db_session: AsyncSession, test_user, test_book):
    """Test getting book rating summary."""
    # Create multiple reviews with different ratings
    ratings = [3.0, 4.0, 5.0, 4.5]
    for rating in ratings:
        review_data = ReviewCreate(
            review_text=f"Review with rating {rating}",
            rating=rating,
        )
        await ReviewService.create_review(
            db_session, test_book.id, test_user.id, review_data
        )

    avg_rating, total_reviews = await ReviewService.get_book_rating_summary(
        db_session, test_book.id
    )

    assert total_reviews == 4
    assert abs(avg_rating - 4.125) < 0.01  # Average of ratings


@pytest.mark.asyncio
async def test_get_rating_summary_no_reviews(db_session: AsyncSession, test_book):
    """Test getting rating summary for book with no reviews."""
    avg_rating, total_reviews = await ReviewService.get_book_rating_summary(
        db_session, test_book.id
    )

    assert avg_rating == 0.0
    assert total_reviews == 0
