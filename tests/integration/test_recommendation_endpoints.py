"""
Integration tests for recommendation endpoints.

This module tests the recommendation and AI summary
endpoints through the API.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
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
async def test_books(db_session):
    """Create test books."""
    books = []
    for genre in ["Fiction", "Fiction", "Mystery", "Sci-Fi"]:
        book_data = BookCreate(
            title=f"Book in {genre}",
            author="Test Author",
            genre=genre,
        )
        books.append(await BookService.create_book(db_session, book_data))
    return books


@pytest.mark.asyncio
async def test_generate_summary(test_client: AsyncClient, auth_token: str, mock_llm_service):
    """Test generating a book summary."""
    with patch('src.routes.recommendation_routes.llm_service', mock_llm_service):
        response = await test_client.post(
            "/ai/generate-summary",
            json={
                "title": "The Great Gatsby",
                "author": "F. Scott Fitzgerald",
                "content": "A long content about the great gatsby...",
                "max_tokens": 1024,
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "generated_at" in data


@pytest.mark.asyncio
async def test_get_recommendations(test_client: AsyncClient, test_books, auth_token: str):
    """Test getting recommendations."""
    response = await test_client.post(
        "/ai/recommendations",
        json={
            "user_id": 1,
            "genre": "Fiction",
            "limit": 5,
            "based_on_reviews": False,
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "criteria" in data
    assert "generated_at" in data


@pytest.mark.asyncio
async def test_get_recommendations_by_genre(test_client: AsyncClient, test_books, auth_token: str):
    """Test getting recommendations by genre."""
    response = await test_client.get(
        "/ai/recommendations/genre/Fiction?limit=5",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert data["genre"] == "Fiction"
    assert len(data["recommendations"]) == 2  # 2 Fiction books


@pytest.mark.asyncio
async def test_get_popular_books(test_client: AsyncClient, test_books, auth_token: str):
    """Test getting popular books."""
    response = await test_client.get(
        "/ai/recommendations/popular?limit=5",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert "criteria" in data
    assert "popular" in data["criteria"].lower()


@pytest.mark.asyncio
async def test_get_similar_books(test_client: AsyncClient, test_books, auth_token: str):
    """Test getting similar books."""
    fiction_book = test_books[0]

    response = await test_client.get(
        f"/ai/recommendations/similar/{fiction_book.id}?limit=5",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data
    assert data["reference_book"] == fiction_book.title
    # Should return other fiction books
    assert len(data["recommendations"]) <= 5


@pytest.mark.asyncio
async def test_get_similar_books_nonexistent(test_client: AsyncClient, auth_token: str):
    """Test getting similar books for non-existent book fails."""
    response = await test_client.get(
        "/ai/recommendations/similar/999?limit=5",
        headers={"Authorization": f"Bearer {auth_token}"}
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_endpoints_require_auth(test_client: AsyncClient):
    """Test that AI endpoints require authentication."""
    endpoints = [
        "/ai/generate-summary",
        "/ai/recommendations",
        "/ai/recommendations/genre/Fiction",
        "/ai/recommendations/popular",
        "/ai/recommendations/similar/1",
    ]

    for endpoint in endpoints:
        if endpoint in ["/ai/generate-summary", "/ai/recommendations"]:
            response = await test_client.post(endpoint, json={})
        else:
            response = await test_client.get(endpoint)

        # Should fail without auth
        assert response.status_code in [401, 403]
