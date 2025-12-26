"""
Application configuration module.

This module handles all configuration settings for the book management system,
including database credentials, JWT settings, and API configuration.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings and configuration.

    Loads configuration from environment variables with sensible defaults.
    """

    # API Configuration
    api_title: str = Field(default="Book Management System API",
                          description="Title of the API")
    api_version: str = Field(default="1.0.0",
                            description="Version of the API")
    api_description: str = Field(
        default="Intelligent book management system with AI-powered summaries and recommendations",
        description="Description of the API"
    )
    debug: bool = Field(default=False, description="Debug mode")

    # Database Configuration
    database_url: str = Field(..., description="Async PostgreSQL database URL")
    database_sync_url: str = Field(..., description="Synchronous PostgreSQL database URL for Alembic migrations")
    database_echo: bool = Field(default=False, description="Log SQL queries")

    # JWT Configuration
    secret_key: str = Field(..., min_length=32, description="Secret key for JWT token signing")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration time in minutes")
    refresh_token_expire_days: int = Field(default=7, description="Refresh token expiration time in days")

    # Groq/LLM Configuration
    groq_api_key: str = Field(..., description="Groq API key for LLM integration")
    llm_model: str = Field(default="llama-3.3-70b-versatile", description="LLM model to use")
    max_tokens: int = Field(default=1024, description="Maximum tokens for LLM generation")

    # CORS Configuration
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )

    # Pagination
    default_page_size: int = Field(default=10,
                                  description="Default page size")
    max_page_size: int = Field(default=100,
                              description="Maximum page size")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
