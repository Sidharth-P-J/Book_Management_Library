"""
LLM and AI integration utilities.

This module provides integration with Groq API for accessing Llama3
and other open-source models for generating summaries and recommendations.
"""

import logging
from typing import Optional
from groq import Groq

from src.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with LLM models via Groq API.

    Uses Groq's API to access Llama3 and other open-source models
    for generating summaries and recommendations.
    """

    def __init__(self):
        """Initialize LLM service with Groq client."""
        if not settings.groq_api_key:
            logger.warning("Groq API key not configured. LLM features will be disabled.")
            self.client = None
        else:
            self.client = Groq(api_key=settings.groq_api_key)

    def generate_summary(
        self,
        title: str,
        author: str,
        content: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a summary for book content.

        Args:
            title: Book title
            author: Book author
            content: Book content or description
            max_tokens: Maximum tokens in response (default from config)

        Returns:
            Generated summary string

        Raises:
            RuntimeError: If LLM service is not configured
        """
        if not self.client:
            raise RuntimeError("LLM service not configured. Please set GROQ_API_KEY environment variable.")

        max_tokens = max_tokens or settings.max_tokens

        prompt = f"""
        Generate a concise summary for the following book content.
        The summary should be 2-3 sentences and capture the main ideas.

        Book Title: {title}
        Author: {author}

        Content:
        {content}

        Summary:
        """

        try:
            message = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt.strip()
                    }
                ],
                model=settings.llm_model,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return message.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise RuntimeError(f"Failed to generate summary: {str(e)}") from e

    def generate_review_summary(
        self,
        book_title: str,
        reviews: list,
        average_rating: float,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a summary of reviews for a book.

        Args:
            book_title: Title of the book
            reviews: List of review texts
            average_rating: Average rating of the book
            max_tokens: Maximum tokens in response

        Returns:
            Generated review summary

        Raises:
            RuntimeError: If LLM service is not configured
        """
        if not self.client:
            raise RuntimeError("LLM service not configured. Please set GROQ_API_KEY environment variable.")

        max_tokens = max_tokens or settings.max_tokens

        # Prepare review text
        reviews_text = "\n".join([f"- {review}" for review in reviews[:5]])  # Use first 5 reviews

        prompt = f"""
        Summarize the following reviews for the book "{book_title}".
        The book has an average rating of {average_rating}/5.
        Provide key insights about what readers liked and disliked.

        Reviews:
        {reviews_text}

        Summary:
        """

        try:
            message = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt.strip()
                    }
                ],
                model=settings.llm_model,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return message.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating review summary: {str(e)}")
            raise RuntimeError(f"Failed to generate review summary: {str(e)}") from e

    def generate_recommendations(
        self,
        user_preferences: str,
        available_books: list,
        limit: int = 5,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate book recommendations based on user preferences.

        Args:
            user_preferences: Description of user preferences
            available_books: List of available books with metadata
            limit: Number of recommendations to generate
            max_tokens: Maximum tokens in response

        Returns:
            Generated recommendations

        Raises:
            RuntimeError: If LLM service is not configured
        """
        if not self.client:
            raise RuntimeError("LLM service not configured. Please set GROQ_API_KEY environment variable.")

        max_tokens = max_tokens or settings.max_tokens

        books_text = "\n".join([
            f"- {book.get('title', 'Unknown')} by {book.get('author', 'Unknown')} (Genre: {book.get('genre', 'Unknown')})"
            for book in available_books[:20]
        ])

        prompt = f"""
        Based on the user preferences below, recommend {limit} books from the available list.
        Provide a brief explanation for each recommendation.

        User Preferences:
        {user_preferences}

        Available Books:
        {books_text}

        Recommendations:
        """

        try:
            message = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt.strip()
                    }
                ],
                model=settings.llm_model,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return message.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise RuntimeError(f"Failed to generate recommendations: {str(e)}") from e


# Global LLM service instance
llm_service = LLMService()
