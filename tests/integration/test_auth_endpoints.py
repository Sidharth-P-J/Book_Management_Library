"""
Integration tests for authentication endpoints.

This module tests the full authentication flow including
registration, login, and profile access.
"""

import pytest
from httpx import AsyncClient
from src.services import UserService
from src.schemas import UserCreate


@pytest.mark.asyncio
async def test_register_user(test_client: AsyncClient):
    """Test user registration."""
    response = await test_client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePassword123",
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_user(test_client: AsyncClient, db_session):
    """Test registering a duplicate user fails."""
    # Create first user
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )
    await UserService.create_user(db_session, user_data)

    # Try to register with same username
    response = await test_client.post(
        "/auth/register",
        json={
            "username": "testuser",
            "email": "different@example.com",
            "password": "SecurePassword123",
        }
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(test_client: AsyncClient, db_session):
    """Test successful login."""
    # Create user
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )
    await UserService.create_user(db_session, user_data)

    # Login
    response = await test_client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "TestPassword123",
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(test_client: AsyncClient, db_session):
    """Test login with wrong password fails."""
    # Create user
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )
    await UserService.create_user(db_session, user_data)

    # Try login with wrong password
    response = await test_client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "WrongPassword",
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(test_client: AsyncClient):
    """Test login with non-existent user fails."""
    response = await test_client.post(
        "/auth/login",
        json={
            "username": "nonexistent",
            "password": "password",
        }
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(test_client: AsyncClient, db_session):
    """Test getting current user profile."""
    # Create user
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )
    user = await UserService.create_user(db_session, user_data)

    # Login and get token
    login_response = await test_client.post(
        "/auth/login",
        json={
            "username": "testuser",
            "password": "TestPassword123",
        }
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = await test_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_current_user_without_auth(test_client: AsyncClient):
    """Test accessing protected endpoint without authentication fails."""
    response = await test_client.get("/auth/me")
    assert response.status_code == 403  # or 401 depending on implementation


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token(test_client: AsyncClient):
    """Test accessing protected endpoint with invalid token fails."""
    response = await test_client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
