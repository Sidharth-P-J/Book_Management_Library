"""
Unit tests for the User service.

This module tests user creation, authentication,
and retrieval operations.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.services import UserService
from src.schemas import UserCreate
from src.auth import verify_password


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a new user."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )

    user = await UserService.create_user(db_session, user_data)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert verify_password("TestPassword123", user.hashed_password)
    assert user.is_active == 1


@pytest.mark.asyncio
async def test_create_duplicate_user(db_session: AsyncSession):
    """Test that creating a duplicate user raises an error."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )

    await UserService.create_user(db_session, user_data)

    # Try to create with same username
    with pytest.raises(ValueError):
        await UserService.create_user(db_session, user_data)


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession):
    """Test retrieving a user by ID."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )

    created_user = await UserService.create_user(db_session, user_data)
    retrieved_user = await UserService.get_user_by_id(db_session, created_user.id)

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == "testuser"


@pytest.mark.asyncio
async def test_get_nonexistent_user(db_session: AsyncSession):
    """Test retrieving a non-existent user returns None."""
    user = await UserService.get_user_by_id(db_session, 999)
    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_username(db_session: AsyncSession):
    """Test retrieving a user by username."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )

    created_user = await UserService.create_user(db_session, user_data)
    retrieved_user = await UserService.get_user_by_username(db_session, "testuser")

    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.username == "testuser"


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session: AsyncSession):
    """Test successful user authentication."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )

    await UserService.create_user(db_session, user_data)
    user, tokens = await UserService.authenticate_user(
        db_session, "testuser", "TestPassword123"
    )

    assert user is not None
    assert user.username == "testuser"
    assert tokens is not None
    assert len(tokens) == 2  # access_token and refresh_token


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session: AsyncSession):
    """Test authentication with wrong password."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )

    await UserService.create_user(db_session, user_data)
    user, tokens = await UserService.authenticate_user(
        db_session, "testuser", "WrongPassword"
    )

    assert user is None
    assert tokens is None


@pytest.mark.asyncio
async def test_authenticate_nonexistent_user(db_session: AsyncSession):
    """Test authentication of non-existent user."""
    user, tokens = await UserService.authenticate_user(
        db_session, "nonexistent", "password"
    )

    assert user is None
    assert tokens is None


@pytest.mark.asyncio
async def test_get_all_users(db_session: AsyncSession):
    """Test retrieving all users with pagination."""
    # Create multiple users
    for i in range(5):
        user_data = UserCreate(
            username=f"testuser{i}",
            email=f"test{i}@example.com",
            password="TestPassword123",
        )
        await UserService.create_user(db_session, user_data)

    users, total = await UserService.get_all_users(db_session, skip=0, limit=10)

    assert len(users) == 5
    assert total == 5


@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession):
    """Test deleting a user."""
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        password="TestPassword123",
    )

    created_user = await UserService.create_user(db_session, user_data)
    success = await UserService.delete_user(db_session, created_user.id)

    assert success is True

    deleted_user = await UserService.get_user_by_id(db_session, created_user.id)
    assert deleted_user is None


@pytest.mark.asyncio
async def test_delete_nonexistent_user(db_session: AsyncSession):
    """Test deleting a non-existent user returns False."""
    success = await UserService.delete_user(db_session, 999)
    assert success is False
