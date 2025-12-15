"""
Integration tests for book endpoints.

This module tests the full book CRUD operations
through the API.
"""

import pytest
from httpx import AsyncClient
from src.services import UserService
from src.schemas import UserCreate, BookCreate
from src.services import BookService


@pytest.fixture
async def auth_token(test_client: AsyncClient, db_session):
    """Create a user and return auth token."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )
    await UserService.create_user(db_session, user_data)

    response = await test_client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "TestPassword123",
        }
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_book(test_client: AsyncClient, auth_token: str):
    """Test creating a book."""
    response = await test_client.post(
        "/books",
        json={
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "genre": "Fiction",
            "year_published": 1925,
            "summary": "A classic novel",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "The Great Gatsby"
    assert data["author"] == "F. Scott Fitzgerald"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_book_without_auth(test_client: AsyncClient):
    """Test creating book without authentication fails."""
    response = await test_client.post(
        "/books",
        json={
            "title": "The Great Gatsby",
            "author": "F. Scott Fitzgerald",
            "genre": "Fiction",
        }
    )

    assert response.status_code == 403  # or 401


@pytest.mark.asyncio
async def test_get_all_books(test_client: AsyncClient, db_session):
    """Test getting all books."""
    # Create books
    for i in range(3):
        book_data = BookCreate(
            title=f"Book {i}",
            author=f"Author {i}",
            genre="Fiction",
        )
        await BookService.create_book(db_session, book_data)

    response = await test_client.get("/books")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_get_books_with_pagination(test_client: AsyncClient, db_session):
    """Test getting books with pagination."""
    # Create books
    for i in range(15):
        book_data = BookCreate(
            title=f"Book {i}",
            author=f"Author {i}",
            genre="Fiction",
        )
        await BookService.create_book(db_session, book_data)

    response = await test_client.get("/books?skip=0&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 10
    assert data["total"] == 15
    assert data["total_pages"] == 2


@pytest.mark.asyncio
async def test_get_books_with_genre_filter(test_client: AsyncClient, db_session):
    """Test getting books with genre filter."""
    # Create books with different genres
    for genre in ["Fiction", "Mystery", "Fiction", "Sci-Fi"]:
        book_data = BookCreate(
            title=f"Book in {genre}",
            author="Author",
            genre=genre,
        )
        await BookService.create_book(db_session, book_data)

    response = await test_client.get("/books?genre=Fiction")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert all(book["genre"] == "Fiction" for book in data["items"])


@pytest.mark.asyncio
async def test_get_book_by_id(test_client: AsyncClient, db_session):
    """Test getting a specific book."""
    book_data = BookCreate(
        title="The Great Gatsby",
        author="F. Scott Fitzgerald",
        genre="Fiction",
    )
    book = await BookService.create_book(db_session, book_data)

    response = await test_client.get(f"/books/{book.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "The Great Gatsby"
    assert data["author"] == "F. Scott Fitzgerald"


@pytest.mark.asyncio
async def test_get_nonexistent_book(test_client: AsyncClient):
    """Test getting non-existent book fails."""
    response = await test_client.get("/books/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_book(test_client: AsyncClient, db_session, auth_token: str):
    """Test updating a book."""
    # Create book
    book_data = BookCreate(
        title="Original Title",
        author="Original Author",
        genre="Fiction",
    )
    book = await BookService.create_book(db_session, book_data)

    # Update book
    response = await test_client.put(
        f"/books/{book.id}",
        json={
            "title": "Updated Title",
            "author": "Updated Author",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["author"] == "Updated Author"
    assert data["genre"] == "Fiction"  # Unchanged


@pytest.mark.asyncio
async def test_delete_book(test_client: AsyncClient, db_session, auth_token: str):
    """Test deleting a book."""
    # Create book
    book_data = BookCreate(
        title="Book to Delete",
        author="Author",
        genre="Fiction",
    )
    book = await BookService.create_book(db_session, book_data)

    # Delete book
    response = await test_client.delete(
        f"/books/{book.id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 204

    # Verify deletion
    verify_response = await test_client.get(f"/books/{book.id}")
    assert verify_response.status_code == 404


@pytest.mark.asyncio
async def test_search_books(test_client: AsyncClient, db_session):
    """Test searching books."""
    # Create books
    books_to_create = [
        ("The Great Gatsby", "F. Scott Fitzgerald"),
        ("To Kill a Mockingbird", "Harper Lee"),
        ("1984", "George Orwell"),
    ]

    for title, author in books_to_create:
        book_data = BookCreate(
            title=title,
            author=author,
            genre="Fiction",
        )
        await BookService.create_book(db_session, book_data)

    # Search by title
    response = await test_client.get("/books/search/Gatsby")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "The Great Gatsby"

    # Search by author
    response = await test_client.get("/books/search/Harper")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["author"] == "Harper Lee"
