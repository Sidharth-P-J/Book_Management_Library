"""
Integration tests for review endpoints.

This module tests the full review CRUD operations
through the API.
"""

import pytest
from httpx import AsyncClient
from src.services import UserService, BookService
from src.schemas import UserCreate, BookCreate


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


@pytest.fixture
async def test_book(db_session):
    """Create a test book."""
    book_data = BookCreate(
        title="Test Book",
        author="Test Author",
        genre="Fiction",
    )
    return await BookService.create_book(db_session, book_data)


@pytest.mark.asyncio
async def test_create_review(test_client: AsyncClient, test_book, auth_token: str):
    """Test creating a review."""
    response = await test_client.post(
        f"/books/{test_book.id}/reviews",
        json={
            "review_text": "Great book!",
            "rating": 4.5,
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["review_text"] == "Great book!"
    assert data["rating"] == 4.5


@pytest.mark.asyncio
async def test_create_review_for_nonexistent_book(test_client: AsyncClient, auth_token: str):
    """Test creating a review for non-existent book fails."""
    response = await test_client.post(
        "/books/999/reviews",
        json={
            "review_text": "Great book!",
            "rating": 4.5,
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_book_reviews(test_client: AsyncClient, db_session, test_book, auth_token: str):
    """Test getting reviews for a book."""
    # Create multiple reviews
    for i in range(3):
        await test_client.post(
            f"/books/{test_book.id}/reviews",
            json={
                "review_text": f"Review {i}",
                "rating": 3.0 + i,
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

    response = await test_client.get(f"/books/{test_book.id}/reviews")

    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 3
    assert data["total"] == 3


@pytest.mark.asyncio
async def test_get_book_summary(test_client: AsyncClient, test_book, auth_token: str):
    """Test getting book review summary."""
    # Create a review first
    await test_client.post(
        f"/books/{test_book.id}/reviews",
        json={
            "review_text": "Great book!",
            "rating": 5.0,
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    response = await test_client.get(f"/books/{test_book.id}/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["book_id"] == test_book.id
    assert data["book_title"] == test_book.title
    assert data["total_reviews"] == 1
    assert data["average_rating"] == 5.0


@pytest.mark.asyncio
async def test_get_summary_no_reviews(test_client: AsyncClient, test_book):
    """Test getting summary for book with no reviews."""
    response = await test_client.get(f"/books/{test_book.id}/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["total_reviews"] == 0
    assert data["average_rating"] == 0.0


@pytest.mark.asyncio
async def test_update_review(test_client: AsyncClient, test_book, auth_token: str):
    """Test updating a review."""
    # Create review
    create_response = await test_client.post(
        f"/books/{test_book.id}/reviews",
        json={
            "review_text": "Original review",
            "rating": 3.0,
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    review_id = create_response.json()["id"]

    # Update review
    response = await test_client.put(
        f"/books/reviews/{review_id}",
        json={
            "review_text": "Updated review",
            "rating": 5.0,
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["review_text"] == "Updated review"
    assert data["rating"] == 5.0


@pytest.mark.asyncio
async def test_delete_review(test_client: AsyncClient, test_book, auth_token: str):
    """Test deleting a review."""
    # Create review
    create_response = await test_client.post(
        f"/books/{test_book.id}/reviews",
        json={
            "review_text": "Review to delete",
            "rating": 3.0,
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    review_id = create_response.json()["id"]

    # Delete review
    response = await test_client.delete(
        f"/books/reviews/{review_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 204
