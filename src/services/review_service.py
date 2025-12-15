"""
Review service for review management operations.

This module contains business logic for creating, retrieving, updating,
and deleting book reviews.
"""

import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.models import Review
from src.schemas import ReviewCreate, ReviewUpdate

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for review management operations."""

    @staticmethod
    async def create_review(
        session: AsyncSession, book_id: int, user_id: int, review_data: ReviewCreate
    ) -> Review:
        """
        Create a new review for a book.

        Args:
            session: Database session
            book_id: Book ID
            user_id: User ID
            review_data: Review creation data

        Returns:
            Created review instance
        """
        review = Review(
            book_id=book_id,
            user_id=user_id,
            review_text=review_data.review_text,
            rating=review_data.rating,
        )

        session.add(review)
        await session.commit()
        await session.refresh(review)

        logger.info(f"Review created for book {book_id} by user {user_id}")
        return review

    @staticmethod
    async def get_review_by_id(session: AsyncSession, review_id: int) -> Optional[Review]:
        """
        Get review by ID.

        Args:
            session: Database session
            review_id: Review ID

        Returns:
            Review instance or None
        """
        stmt = select(Review).where(Review.id == review_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_reviews_by_book(
        session: AsyncSession,
        book_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[Review], int]:
        """
        Get all reviews for a book with pagination.

        Args:
            session: Database session
            book_id: Book ID
            skip: Number of records to skip
            limit: Number of records to fetch

        Returns:
            Tuple of (reviews list, total count)
        """
        # Get total count
        count_stmt = select(func.count(Review.id)).where(Review.book_id == book_id)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = select(Review).where(Review.book_id == book_id).offset(skip).limit(limit)
        result = await session.execute(stmt)
        reviews = result.scalars().all()

        return list(reviews), total

    @staticmethod
    async def get_reviews_by_user(
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[Review], int]:
        """
        Get all reviews by a user with pagination.

        Args:
            session: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Number of records to fetch

        Returns:
            Tuple of (reviews list, total count)
        """
        # Get total count
        count_stmt = select(func.count(Review.id)).where(Review.user_id == user_id)
        count_result = await session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Get paginated results
        stmt = select(Review).where(Review.user_id == user_id).offset(skip).limit(limit)
        result = await session.execute(stmt)
        reviews = result.scalars().all()

        return list(reviews), total

    @staticmethod
    async def update_review(
        session: AsyncSession, review_id: int, review_data: ReviewUpdate
    ) -> Optional[Review]:
        """
        Update a review.

        Args:
            session: Database session
            review_id: Review ID
            review_data: Review update data

        Returns:
            Updated review instance or None
        """
        review = await ReviewService.get_review_by_id(session, review_id)
        if not review:
            return None

        # Update only provided fields
        update_data = review_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(review, key, value)

        await session.commit()
        await session.refresh(review)

        logger.info(f"Review updated: {review_id}")
        return review

    @staticmethod
    async def delete_review(session: AsyncSession, review_id: int) -> bool:
        """
        Delete a review by ID.

        Args:
            session: Database session
            review_id: Review ID

        Returns:
            True if deleted, False if not found
        """
        review = await ReviewService.get_review_by_id(session, review_id)
        if not review:
            return False

        await session.delete(review)
        await session.commit()

        logger.info(f"Review deleted: {review_id}")
        return True

    @staticmethod
    async def get_book_rating_summary(
        session: AsyncSession, book_id: int
    ) -> tuple[float, int]:
        """
        Get average rating and total review count for a book.

        Args:
            session: Database session
            book_id: Book ID

        Returns:
            Tuple of (average_rating, total_reviews)
        """
        stmt = select(
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("total_reviews")
        ).where(Review.book_id == book_id)

        result = await session.execute(stmt)
        avg_rating, total_reviews = result.one()

        return float(avg_rating) if avg_rating else 0.0, total_reviews or 0
