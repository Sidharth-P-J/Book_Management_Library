"""
Unit tests for the Book service.

This module tests book CRUD operations,
filtering, and searching.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import BookService
from src.schemas import BookCreate, BookUpdate


@pytest.mark.asyncio
async def test_create_book(db_session: AsyncSession):
    """Test creating a new book."""
    book_data = BookCreate(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        genre="Fiction",
        year_published=1925,
        summary="A classic novel about the American Dream.",
    )

    book = await BookService.create_book(db_session, book_data)

    assert book.id is not None
    assert book.title == "The Great Gatsby"
    assert book.author == "F. Scott Fitzgerald"
    assert book.genre == "Fiction"
    assert book.year_published == 1925


@pytest.mark.asyncio
async def test_get_book_by_id(db_session: AsyncSession):
    """Test retrieving a book by ID."""
    book_data = BookCreate(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        genre="Fiction",
        year_published=1925,
        summary="A classic novel.",
    )

    created_book = await BookService.create_book(db_session, book_data)
    retrieved_book = await BookService.get_book_by_id(db_session, created_book.id)

    assert retrieved_book is not None
    assert retrieved_book.id == created_book.id
    assert retrieved_book.title == "The Great Gatsby"


@pytest.mark.asyncio
async def test_get_nonexistent_book(db_session: AsyncSession):
    """Test retrieving a non-existent book returns None."""
    book = await BookService.get_book_by_id(db_session, 999)
    assert book is None


@pytest.mark.asyncio
async def test_get_all_books(db_session: AsyncSession):
    """Test retrieving all books with pagination."""
    # Create multiple books
    for i in range(5):
        book_data = BookCreate(
            title=f"Book {i}",
            author=f"Author {i}",
            genre="Fiction",
            year_published=2020 + i,
        )
        await BookService.create_book(db_session, book_data)

    books, total = await BookService.get_all_books(db_session, skip=0, limit=10)

    assert len(books) == 5
    assert total == 5


@pytest.mark.asyncio
async def test_get_books_with_genre_filter(db_session: AsyncSession):
    """Test retrieving books filtered by genre."""
    # Create books with different genres
    for genre in ["Fiction", "Mystery", "Fiction"]:
        book_data = BookCreate(
            title=f"Book in {genre}",
            author="Author",
            genre=genre,
        )
        await BookService.create_book(db_session, book_data)

    books, total = await BookService.get_all_books(
        db_session, skip=0, limit=10, genre="Fiction"
    )

    assert len(books) == 2
    assert total == 2
    assert all(book.genre == "Fiction" for book in books)


@pytest.mark.asyncio
async def test_get_books_with_author_filter(db_session: AsyncSession):
    """Test retrieving books filtered by author."""
    # Create books by different authors
    for author in ["Author A", "Author B", "Author A"]:
        book_data = BookCreate(
            title="Book Title",
            author=author,
            genre="Fiction",
        )
        await BookService.create_book(db_session, book_data)

    books, total = await BookService.get_all_books(
        db_session, skip=0, limit=10, author="Author A"
    )

    assert len(books) == 2
    assert total == 2
    assert all(book.author == "Author A" for book in books)


@pytest.mark.asyncio
async def test_update_book(db_session: AsyncSession):
    """Test updating a book."""
    book_data = BookCreate(
        title="Original Title",
        author="Original Author",
        genre="Fiction",
    )

    created_book = await BookService.create_book(db_session, book_data)

    update_data = BookUpdate(
        title="Updated Title",
        author="Updated Author",
    )

    updated_book = await BookService.update_book(
        db_session, created_book.id, update_data
    )

    assert updated_book is not None
    assert updated_book.title == "Updated Title"
    assert updated_book.author == "Updated Author"
    assert updated_book.genre == "Fiction"  # Unchanged


@pytest.mark.asyncio
async def test_update_nonexistent_book(db_session: AsyncSession):
    """Test updating a non-existent book returns None."""
    update_data = BookUpdate(title="Updated Title")
    updated_book = await BookService.update_book(db_session, 999, update_data)
    assert updated_book is None


@pytest.mark.asyncio
async def test_delete_book(db_session: AsyncSession):
    """Test deleting a book."""
    book_data = BookCreate(
        title="Book to Delete",
        author="Author",
        genre="Fiction",
    )

    created_book = await BookService.create_book(db_session, book_data)
    success = await BookService.delete_book(db_session, created_book.id)

    assert success is True

    deleted_book = await BookService.get_book_by_id(db_session, created_book.id)
    assert deleted_book is None


@pytest.mark.asyncio
async def test_delete_nonexistent_book(db_session: AsyncSession):
    """Test deleting a non-existent book returns False."""
    success = await BookService.delete_book(db_session, 999)
    assert success is False


@pytest.mark.asyncio
async def test_search_books_by_title(db_session: AsyncSession):
    """Test searching books by title."""
    # Create books
    book_data1 = BookCreate(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        genre="Fiction",
    )
    book_data2 = BookCreate(
        title="To Kill a Mockingbird",
        author="Harper Lee",
        genre="Fiction",
    )

    await BookService.create_book(db_session, book_data1)
    await BookService.create_book(db_session, book_data2)

    books, total = await BookService.search_books(db_session, "Gatsby")

    assert len(books) == 1
    assert total == 1
    assert books[0].title == "The Great Gatsby"


@pytest.mark.asyncio
async def test_search_books_by_author(db_session: AsyncSession):
    """Test searching books by author."""
    # Create books
    book_data1 = BookCreate(
        title="Book 1",
        author="F. Scott Fitzgerald",
        genre="Fiction",
    )
    book_data2 = BookCreate(
        title="Book 2",
        author="Harper Lee",
        genre="Fiction",
    )

    await BookService.create_book(db_session, book_data1)
    await BookService.create_book(db_session, book_data2)

    books, total = await BookService.search_books(db_session, "Fitzgerald")

    assert len(books) == 1
    assert total == 1
    assert books[0].author == "F. Scott Fitzgerald"
