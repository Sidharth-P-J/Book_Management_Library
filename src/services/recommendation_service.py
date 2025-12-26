"""
Recommendation service for generating book recommendations.

This module contains business logic for generating personalized
book recommendations based on user preferences and reading history.
"""

import logging
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from src.models import Book, Review
from src.utils.llm import llm_service

logger = logging.getLogger(__name__)


class RecommendationService:
    """Service for generating book recommendations."""

    @staticmethod
    async def get_recommendations_by_genre(
        session: AsyncSession,
        genre: str,
        limit: int = 5,
        exclude_book_ids: List[int] = None,
    ) -> List[Book]:
        """
        Get book recommendations by genre.

        Args:
            session: Database session
            genre: Genre to recommend
            limit: Number of recommendations
            exclude_book_ids: Book IDs to exclude from results

        Returns:
            List of recommended books
        """
        query = select(Book).where(Book.genre.ilike(f"%{genre}%"))

        if exclude_book_ids:
            query = query.where(Book.id.notin_(exclude_book_ids))

        query = query.limit(limit)
        result = await session.execute(query)
        books = result.scalars().all()

        return list(books)

    @staticmethod
    async def get_popular_books(
        session: AsyncSession,
        limit: int = 5,
        min_reviews: int = 2,
    ) -> List[Book]:
        """
        Get popular books based on average rating.

        Args:
            session: Database session
            limit: Number of recommendations
            min_reviews: Minimum number of reviews required

        Returns:
            List of popular books
        """
        # Subquery to get books with their average rating
        subquery = select(
            Review.book_id,
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count")
        ).group_by(Review.book_id).subquery()

        query = select(Book).join(
            subquery, Book.id == subquery.c.book_id
        ).where(
            subquery.c.review_count >= min_reviews
        ).order_by(
            subquery.c.avg_rating.desc()
        ).limit(limit)

        result = await session.execute(query)
        books = result.scalars().all()

        return list(books)

    @staticmethod
    async def get_similar_books(
        session: AsyncSession,
        book_id: int,
        limit: int = 5,
    ) -> List[Book]:
        """
        Get books similar to a given book (same genre).

        Args:
            session: Database session
            book_id: Reference book ID
            limit: Number of recommendations

        Returns:
            List of similar books
        """
        # Get the reference book
        from src.services.book_service import BookService
        book = await BookService.get_book_by_id(session, book_id)

        if not book:
            return []

        # Get similar books
        query = select(Book).where(
            and_(Book.genre == book.genre, Book.id != book_id)
        ).limit(limit)

        result = await session.execute(query)
        books = result.scalars().all()

        return list(books)

    @staticmethod
    async def get_recommendations_with_llm(
        session: AsyncSession,
        user_preferences: str,
        limit: int = 5,
    ) -> tuple[List[Book], str]:
        """
        Generate recommendations using LLM based on user preferences.

        Args:
            session: Database session
            user_preferences: Description of user preferences
            limit: Number of recommendations

        Returns:
            Tuple of (recommended books, LLM reasoning)
        """
        try:
            # Get all available books
            stmt = select(Book).limit(100)
            result = await session.execute(stmt)
            available_books = result.scalars().all()

            # Convert to dictionary format for LLM
            books_data = [
                {
                    "title": book.title,
                    "author": book.author,
                    "genre": book.genre,
                    "id": book.id,
                    "average_rating": book.average_rating or 0,
                }
                for book in available_books
            ]

            # Generate recommendations using LLM
            reasoning = await llm_service.generate_recommendations(
                user_preferences, books_data, limit
            )

            # For demonstration, return top books by rating
            query = select(Book).order_by(Book.id).limit(limit)
            result = await session.execute(query)
            recommended_books = result.scalars().all()

            logger.info(f"Generated {len(recommended_books)} recommendations for user")
            return list(recommended_books), reasoning

        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            # Fallback to popular books if LLM fails
            return await RecommendationService.get_popular_books(session, limit), str(e)

    @staticmethod
    async def get_user_recommendations(
        session: AsyncSession,
        user_id: int,
        limit: int = 5,
    ) -> List[Book]:
        """
        Get recommendations based on user's review history.

        Args:
            session: Database session
            user_id: User ID
            limit: Number of recommendations

        Returns:
            List of recommended books
        """
        # Get genres the user has reviewed positively
        query = select(Book.genre).join(
            Review, Review.book_id == Book.id
        ).where(
            and_(Review.user_id == user_id, Review.rating >= 4)
        ).group_by(Book.genre).limit(3)

        result = await session.execute(query)
        favorite_genres = [row[0] for row in result.all()]

        if not favorite_genres:
            # If no favorite genres, return popular books
            return await RecommendationService.get_popular_books(session, limit)

        # Get books in favorite genres
        recommendations = []
        for genre in favorite_genres:
            books = await RecommendationService.get_recommendations_by_genre(
                session, genre, limit // len(favorite_genres) + 1
            )
            recommendations.extend(books)

        # Remove duplicates and limit
        seen_ids = set()
        unique_recommendations = []
        for book in recommendations:
            if book.id not in seen_ids:
                unique_recommendations.append(book)
                seen_ids.add(book.id)
                if len(unique_recommendations) >= limit:
                    break

        return unique_recommendations
