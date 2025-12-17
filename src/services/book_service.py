"""
Book service for book management operations.

This module contains business logic for CRUD operations on books,
including retrieval, filtering, and pagination.
"""

import logging
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.models import Book
from src.schemas import BookCreate, BookUpdate

logger = logging.getLogger(__name__)


class BookService:
    """Service for book management operations."""

    @staticmethod
    async def create_book(session: AsyncSession, book_data: BookCreate) -> Book:
        """
        Create a new book.

        Args:
            session: Database session
            book_data: Book creation data

        Returns:
            Created book instance
        """
        book = Book(
            title=book_data.title,
            author=book_data.author,
            genre=book_data.genre,
            year_published=book_data.year_published,
            summary=book_data.summary,
        )

        session.add(book)
        await session.commit()
        await session.refresh(book)

        logger.info(f"Book created: {book.title} by {book.author}")
        return book

    @staticmethod
    async def get_book_by_id(session: AsyncSession, book_id: int) -> Optional[Book]:
        """
        Get book by ID.

        Args:
            session: Database session
            book_id: Book ID

        Returns:
            Book instance or None
        """
        stmt = select(Book).options(selectinload(Book.reviews)).where(Book.id == book_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_books(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        genre: Optional[str] = None,
        author: Optional[str] = None,
    ) -> tuple[List[Book], int]:
        """
        Get all books with optional filtering and pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Number of records to fetch
            genre: Optional genre filter
            author: Optional author filter

        Returns:
            Tuple of (books list, total count)
        """
        # Build query
        query = select(Book)

        if genre:
            query = query.where(Book.genre.ilike(f"%{genre}%"))
        if author:
            query = query.where(Book.author.ilike(f"%{author}%"))

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await session.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated results
        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        books = result.scalars().all()

        return list(books), total

    @staticmethod
    async def update_book(
        session: AsyncSession, book_id: int, book_data: BookUpdate
    ) -> Optional[Book]:
        """
        Update a book.

        Args:
            session: Database session
            book_id: Book ID
            book_data: Book update data

        Returns:
            Updated book instance or None
        """
        book = await BookService.get_book_by_id(session, book_id)
        if not book:
            return None

        # Update only provided fields
        update_data = book_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(book, key, value)

        await session.commit()
        await session.refresh(book)

        logger.info(f"Book updated: {book.title}")
        return book

    @staticmethod
    async def delete_book(session: AsyncSession, book_id: int) -> bool:
        """
        Delete a book by ID.

        Args:
            session: Database session
            book_id: Book ID

        Returns:
            True if deleted, False if not found
        """
        book = await BookService.get_book_by_id(session, book_id)
        if not book:
            return False

        await session.delete(book)
        await session.commit()

        logger.info(f"Book deleted: {book_id}")
        return True

    @staticmethod
    async def search_books(
        session: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 10,
    ) -> tuple[List[Book], int]:
        """
        Search books by title or author.

        Args:
            session: Database session
            query: Search query string
            skip: Number of records to skip
            limit: Number of records to fetch

        Returns:
            Tuple of (books list, total count)
        """
        search_query = select(Book).where(
            (Book.title.ilike(f"%{query}%")) | (Book.author.ilike(f"%{query}%"))
        )

        # Get total count
        count_query = select(func.count()).select_from(search_query.subquery())
        count_result = await session.execute(count_query)
        total = count_result.scalar() or 0

        # Get paginated results
        search_query = search_query.offset(skip).limit(limit)
        result = await session.execute(search_query)
        books = result.scalars().all()

        return list(books), total
