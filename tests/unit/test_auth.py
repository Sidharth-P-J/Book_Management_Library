"""
Unit tests for authentication utilities.

This module tests password hashing, token creation,
and token verification.
"""

import pytest
from datetime import datetime, timedelta
from jose import jwt

from src.auth import (
    hash_password,
    verify_password,
    create_tokens,
    verify_token,
)
from src.core.config import settings


def test_hash_password():
    """Test password hashing."""
    password = "TestPassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 0


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "TestPassword123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "TestPassword123"
    hashed = hash_password(password)

    assert verify_password("WrongPassword", hashed) is False


def test_create_tokens():
    """Test token creation."""
    user_id = 1
    username = "testuser"
    role = "user"

    access_token, refresh_token = create_tokens(user_id, username, role)

    assert access_token is not None
    assert refresh_token is not None
    assert len(access_token) > 0
    assert len(refresh_token) > 0


def test_verify_token_valid():
    """Test token verification with valid token."""
    user_id = 1
    username = "testuser"
    role = "user"

    access_token, _ = create_tokens(user_id, username, role)
    payload = verify_token(access_token)

    assert payload["sub"] == str(user_id)
    assert payload["username"] == username
    assert payload["role"] == role


def test_verify_token_invalid():
    """Test token verification with invalid token."""
    invalid_token = "invalid.token.here"

    with pytest.raises(Exception):
        verify_token(invalid_token)


def test_verify_token_expired():
    """Test token verification with expired token."""
    # Create an expired token
    payload = {
        "sub": "1",
        "username": "testuser",
        "exp": datetime.utcnow() - timedelta(hours=1),
    }
    expired_token = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm
    )

    with pytest.raises(Exception):
        verify_token(expired_token)


def test_token_contains_user_info():
    """Test that token contains correct user information."""
    user_id = 42
    username = "john_doe"
    role = "admin"

    access_token, _ = create_tokens(user_id, username, role)
    payload = verify_token(access_token)

    assert payload["sub"] == str(user_id)
    assert payload["username"] == username
    assert payload["role"] == role
    assert payload["type"] == "access"


def test_refresh_token_type():
    """Test that refresh token is correctly marked."""
    _, refresh_token = create_tokens(1, "testuser", "user")
    payload = verify_token(refresh_token)

    assert payload["type"] == "refresh"
