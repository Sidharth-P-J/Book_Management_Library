"""
Authentication routes for user registration and login.

This module provides endpoints for user registration, login,
and token refresh operations.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_db
from src.schemas import UserCreate, UserLogin, TokenResponse, UserResponse
from src.services import UserService
from src.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_db)):
    """
    Register a new user.

    Args:
        user_data: User registration data
        session: Database session

    Returns:
        Created user information

    Raises:
        HTTPException: If user already exists
    """
    try:
        user = await UserService.create_user(session, user_data)
        return user
    except ValueError as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, session: AsyncSession = Depends(get_db)):
    """
    Login a user and return access/refresh tokens.

    Args:
        credentials: Login credentials
        session: Database session

    Returns:
        Access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    user, tokens = await UserService.authenticate_user(
        session, credentials.username, credentials.password
    )

    if not user or not tokens:
        logger.warning(f"Failed login attempt for username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    access_token, refresh_token = tokens
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60,  # 30 minutes in seconds
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
):
    """
    Get current authenticated user's profile.

    Args:
        current_user: Current authenticated user
        session: Database session

    Returns:
        Current user information

    Raises:
        HTTPException: If user not found
    """
    user_id = int(current_user.get("sub"))
    user = await UserService.get_user_by_id(session, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user
