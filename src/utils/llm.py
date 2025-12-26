import logging
import asyncio
from typing import Optional, List, Dict, Any
from groq import Groq
from functools import partial

from src.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for interacting with LLM models via Groq API.
    
    Provides async wrappers around the synchronous Groq client to ensure
    non-blocking operation within the FastAPI event loop.
    """

    def __init__(self):
        """Initialize LLM service with Groq client."""
        # Check if API key is configured (it's mandatory now but good to check)
        if not settings.groq_api_key:
            logger.warning("Groq API key not configured. LLM features will be disabled.")
            self.client = None
        else:
            self.client = Groq(api_key=settings.groq_api_key)

    async def _run_in_thread(self, func, *args, **kwargs):
        """Run a blocking function in a separate thread."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, partial(func, *args, **kwargs))

    async def generate_summary(
        self,
        title: str,
        author: str,
        content: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate a summary for book content asynchronously.

        Args:
            title: Book title
            author: Book author
            content: Book content
            max_tokens: Max tokens (optional)

        Returns:
            Generated summary
        """
        if not self.client:
            raise RuntimeError("LLM service not configured.")

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
            # Run blocking API call in thread pool
            chat_completion = await self._run_in_thread(
                self.client.chat.completions.create,
                messages=[
                    {"role": "user", "content": prompt.strip()}
                ],
                model=settings.llm_model,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to generate summary: {str(e)}") from e

    async def generate_review_summary(
        self,
        book_title: str,
        reviews: list,
        average_rating: float,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate review summary asynchronously."""
        if not self.client:
            raise RuntimeError("LLM service not configured.")

        max_tokens = max_tokens or settings.max_tokens
        
        # Limit reviews to avoid token limits
        reviews_text = "\n".join([f"- {r}" for r in reviews[:10]])

        prompt = f"""
        Summarize the following reviews for the book "{book_title}".
        The book has an average rating of {average_rating}/5.
        Provide key insights about what readers liked and disliked.

        Reviews:
        {reviews_text}

        Summary:
        """

        try:
            chat_completion = await self._run_in_thread(
                self.client.chat.completions.create,
                messages=[
                    {"role": "user", "content": prompt.strip()}
                ],
                model=settings.llm_model,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating review summary: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to generate review summary: {str(e)}") from e

    async def generate_recommendations(
        self,
        user_preferences: str,
        available_books: list,
        limit: int = 5,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate recommendations asynchronously."""
        if not self.client:
            raise RuntimeError("LLM service not configured.")

        max_tokens = max_tokens or settings.max_tokens

        # Format books compactly
        books_text = "\n".join([
            f"- ID:{b.get('id')} Title:{b.get('title')} Genre:{b.get('genre')}"
            for b in available_books[:30]  # Limit context
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
            chat_completion = await self._run_in_thread(
                self.client.chat.completions.create,
                messages=[
                    {"role": "user", "content": prompt.strip()}
                ],
                model=settings.llm_model,
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return chat_completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to generate recommendations: {str(e)}") from e


# Global LLM service instance
llm_service = LLMService()
