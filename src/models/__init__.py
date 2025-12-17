"""
Database models for the book management system.

This module defines the SQLAlchemy ORM models for books, reviews, and users
with all necessary relationships and constraints.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from src.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


class User(Base):
    """
    User model for authentication and authorization.

    Attributes:
        id: Unique identifier for the user
        username: Unique username
        email: Unique email address
        hashed_password: Bcrypt hashed password
        role: User role (admin, user, moderator)
        is_active: Whether user is active
        created_at: Timestamp of user creation
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"


class Book(Base):
    """
    Book model for storing book information.

    Attributes:
        id: Unique identifier for the book
        title: Book title
        author: Book author name
        genre: Book genre
        year_published: Year of publication
        summary: Book summary/description
        created_at: Timestamp of book creation
        updated_at: Timestamp of last update
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    genre = Column(String(100), nullable=False, index=True)
    year_published = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    reviews = relationship("Review", back_populates="book", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Book(id={self.id}, title={self.title}, author={self.author})>"

    @property
    def average_rating(self) -> Optional[float]:
        """Calculate average rating from reviews."""
        if 'reviews' not in self.__dict__:
            return None
        if not self.reviews:
            return None
        total = sum(review.rating for review in self.reviews)
        return round(total / len(self.reviews), 2)


class Review(Base):
    """
    Review model for storing book reviews.

    Attributes:
        id: Unique identifier for the review
        book_id: Foreign key to books table
        user_id: Foreign key to users table
        review_text: Text content of the review
        rating: Numeric rating (1-5)
        created_at: Timestamp of review creation
        updated_at: Timestamp of last update
    """
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    review_text = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)  # Rating should be between 1 and 5
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    book = relationship("Book", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, book_id={self.book_id}, user_id={self.user_id}, rating={self.rating})>"
