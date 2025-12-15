"""
Book management routes.

This module provides endpoints for CRUD operations on books,
including retrieval, filtering, searching, and deletion.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_db
from src.schemas import BookCreate, BookUpdate, BookResponse, BookDetailResponse
from src.services import BookService
from src.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/books", tags=["Books"])


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Create a new book.

    Args:
        book_data: Book creation data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Created book information
    """
    try:
        book = await BookService.create_book(session, book_data)
        logger.info(f"Book created by user {current_user.get('sub')}: {book.title}")
        return book
    except Exception as e:
        logger.error(f"Error creating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.get("", response_model=dict)
async def get_books(
    session: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    genre: Optional[str] = None,
    author: Optional[str] = None,
):
    """
    Get all books with optional filtering and pagination.

    Args:
        session: Database session
        skip: Number of records to skip
        limit: Number of records to fetch
        genre: Optional genre filter
        author: Optional author filter

    Returns:
        Paginated list of books
    """
    books, total = await BookService.get_all_books(
        session, skip=skip, limit=limit, genre=genre, author=author
    )

    return {
        "items": books,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
    }


@router.get("/{book_id}", response_model=BookDetailResponse)
async def get_book(
    book_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Get a specific book by ID with its reviews.

    Args:
        book_id: Book ID
        session: Database session

    Returns:
        Book information with reviews

    Raises:
        HTTPException: If book not found
    """
    book = await BookService.get_book_by_id(session, book_id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update a book's information.

    Args:
        book_id: Book ID
        book_data: Book update data
        session: Database session
        current_user: Current authenticated user

    Returns:
        Updated book information

    Raises:
        HTTPException: If book not found
    """
    try:
        book = await BookService.update_book(session, book_id, book_data)

        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        logger.info(f"Book updated by user {current_user.get('sub')}: {book_id}")
        return book
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating book: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a book by ID.

    Args:
        book_id: Book ID
        session: Database session
        current_user: Current authenticated user

    Raises:
        HTTPException: If book not found
    """
    success = await BookService.delete_book(session, book_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    logger.info(f"Book deleted by user {current_user.get('sub')}: {book_id}")


@router.get("/search/{query}", response_model=dict)
async def search_books(
    query: str,
    session: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Search books by title or author.

    Args:
        query: Search query string
        session: Database session
        skip: Number of records to skip
        limit: Number of records to fetch

    Returns:
        Paginated search results
    """
    books, total = await BookService.search_books(
        session, query, skip=skip, limit=limit
    )

    return {
        "items": books,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
    }
