"""
User service for user management operations.

This module contains business logic for user creation, authentication,
and user profile management.
"""

import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models import User, UserRole
from src.auth import hash_password, verify_password, create_tokens
from src.schemas import UserCreate, UserResponse

logger = logging.getLogger(__name__)


class UserService:
    """Service for user management operations."""

    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
        """
        Create a new user.

        Args:
            session: Database session
            user_data: User creation data

        Returns:
            Created user instance

        Raises:
            ValueError: If username or email already exists
        """
        # Check if user already exists
        stmt = select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
        result = await session.execute(stmt)
        if result.scalar_one_or_none():
            raise ValueError("User with this username or email already exists")

        # Create new user
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            role=UserRole.USER,
            is_active=1,
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

        logger.info(f"User created: {user.username}")
        return user

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            User instance or None
        """
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            session: Database session
            username: Username

        Returns:
            User instance or None
        """
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_user(
        session: AsyncSession, username: str, password: str
    ) -> tuple[Optional[User], Optional[tuple[str, str]]]:
        """
        Authenticate a user and return tokens.

        Args:
            session: Database session
            username: Username
            password: Password

        Returns:
            Tuple of (user, (access_token, refresh_token)) or (None, None)
        """
        user = await UserService.get_user_by_username(session, username)

        if not user or not user.is_active:
            return None, None

        if not verify_password(password, user.hashed_password):
            return None, None

        tokens = create_tokens(user.id, user.username, user.role.value)
        logger.info(f"User authenticated: {user.username}")
        return user, tokens

    @staticmethod
    async def get_all_users(
        session: AsyncSession, skip: int = 0, limit: int = 10
    ) -> tuple[list[User], int]:
        """
        Get all users with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Number of records to fetch

        Returns:
            Tuple of (users list, total count)
        """
        # Get total count
        count_stmt = select(User)
        count_result = await session.execute(count_stmt)
        total = len(count_result.all())

        # Get paginated results
        stmt = select(User).offset(skip).limit(limit)
        result = await session.execute(stmt)
        users = result.scalars().all()

        return list(users), total

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int) -> bool:
        """
        Delete a user by ID.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            True if deleted, False if not found
        """
        user = await UserService.get_user_by_id(session, user_id)
        if not user:
            return False

        await session.delete(user)
        await session.commit()
        logger.info(f"User deleted: {user_id}")
        return True
