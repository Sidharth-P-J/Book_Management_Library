"""
Pydantic schemas for request/response validation.

This module defines all Pydantic models used for request/response serialization
and validation in the API endpoints.
"""

from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from typing import Optional, List


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(..., min_length=8)

    @validator('password')
    def password_strong(cls, v):
        """Validate password strength."""
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(UserBase):
    """User response schema."""
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """User login schema."""
    username: str
    password: str


# ==================== Book Schemas ====================

class BookBase(BaseModel):
    """Base book schema."""
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    genre: str = Field(..., min_length=1, max_length=100)
    year_published: Optional[int] = None
    summary: Optional[str] = None


class BookCreate(BookBase):
    """Book creation schema."""
    pass


class BookUpdate(BaseModel):
    """Book update schema - all fields optional."""
    title: Optional[str] = Field(None, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    genre: Optional[str] = Field(None, max_length=100)
    year_published: Optional[int] = None
    summary: Optional[str] = None


class BookResponse(BookBase):
    """Book response schema."""
    id: int
    created_at: datetime
    updated_at: datetime
    average_rating: Optional[float] = None

    class Config:
        from_attributes = True


class BookDetailResponse(BookResponse):
    """Detailed book response with reviews."""
    reviews: List['ReviewResponse'] = []


# ==================== Review Schemas ====================

class ReviewBase(BaseModel):
    """Base review schema."""
    review_text: str = Field(..., min_length=1, max_length=5000)
    rating: float = Field(..., ge=1, le=5)


class ReviewCreate(ReviewBase):
    """Review creation schema."""
    pass


class ReviewUpdate(BaseModel):
    """Review update schema."""
    review_text: Optional[str] = Field(None, max_length=5000)
    rating: Optional[float] = Field(None, ge=1, le=5)


class ReviewResponse(ReviewBase):
    """Review response schema."""
    id: int
    book_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True


# ==================== Summary Schemas ====================

class SummaryGenerateRequest(BaseModel):
    """Request for generating a summary."""
    title: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1)
    content: str = Field(..., min_length=10)
    max_tokens: Optional[int] = None


class SummaryResponse(BaseModel):
    """Summary response schema."""
    summary: str
    generated_at: datetime


class ReviewSummaryResponse(BaseModel):
    """Review summary response."""
    book_id: int
    book_title: str
    total_reviews: int
    average_rating: float
    summary: str
    generated_at: datetime


# ==================== Recommendation Schemas ====================

class RecommendationRequest(BaseModel):
    """Request for getting recommendations."""
    user_id: int
    genre: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=20)
    based_on_reviews: bool = False


class RecommendationResponse(BaseModel):
    """Recommendation response schema."""
    recommendations: List[BookResponse]
    criteria: str
    generated_at: datetime


# ==================== Auth Schemas ====================

class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefreshRequest(BaseModel):
    """Token refresh request schema."""
    refresh_token: str


# ==================== Pagination Schemas ====================

class PaginatedResponse(BaseModel):
    """Generic paginated response."""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int


# Update forward references
BookDetailResponse.model_rebuild()
