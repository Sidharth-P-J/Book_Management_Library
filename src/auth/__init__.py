"""
Authentication utilities for JWT token handling.

This module provides utilities for JWT token creation, validation,
and password hashing using bcrypt.
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

from src.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer security scheme
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_tokens(user_id: int, username: str, role: str) -> Tuple[str, str]:
    """
    Create access and refresh JWT tokens.

    Args:
        user_id: User ID to encode in token
        username: Username to encode in token
        role: User role for RBAC

    Returns:
        Tuple of (access_token, refresh_token)
    """
    # Access token
    access_payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes),
    }
    access_token = jwt.encode(
        access_payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    # Refresh token
    refresh_payload = {
        "sub": str(user_id),
        "username": username,
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days),
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    return access_token, refresh_token


def verify_token(token: str) -> dict:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    """
    Dependency for getting current authenticated user.

    Args:
        credentials: HTTP credentials from request

    Returns:
        Decoded token payload with user information

    Raises:
        HTTPException: If authentication fails
    """
    return verify_token(credentials.credentials)


def get_current_user_id(current_user: dict = Depends(get_current_user)) -> int:
    """
    Extract and return user ID from current user.

    Args:
        current_user: Current authenticated user from dependency

    Returns:
        User ID
    """
    return int(current_user.get("sub"))


def require_role(required_role: str):
    """
    Dependency factory for role-based access control.

    Args:
        required_role: Required role to access resource

    Returns:
        Dependency function
    """
    async def check_role(current_user: dict = Depends(get_current_user)) -> dict:
        """Check if user has required role."""
        user_role = current_user.get("role")
        if user_role != required_role and user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user

    return check_role
