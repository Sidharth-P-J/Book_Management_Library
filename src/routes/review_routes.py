"""
Review management routes.

This module provides endpoints for creating, retrieving, updating,
and deleting book reviews.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import get_db
from src.schemas import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewSummaryResponse
from src.services import ReviewService, BookService
from src.utils import llm_service
from src.auth import get_current_user, get_current_user_id
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/books", tags=["Reviews"])


@router.post("/{book_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    book_id: int,
    review_data: ReviewCreate,
    session: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create a new review for a book.

    Args:
        book_id: Book ID
        review_data: Review creation data
        session: Database session
        user_id: Current user ID

    Returns:
        Created review information

    Raises:
        HTTPException: If book not found
    """
    try:
        # Check if book exists
        book = await BookService.get_book_by_id(session, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        review = await ReviewService.create_review(
            session, book_id, user_id, review_data
        )
        logger.info(f"Review created for book {book_id} by user {user_id}")
        return review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.get("/{book_id}/reviews", response_model=dict)
async def get_book_reviews(
    book_id: int,
    session: AsyncSession = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Get all reviews for a book with pagination.

    Args:
        book_id: Book ID
        session: Database session
        skip: Number of records to skip
        limit: Number of records to fetch

    Returns:
        Paginated list of reviews

    Raises:
        HTTPException: If book not found
    """
    # Check if book exists
    book = await BookService.get_book_by_id(session, book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    reviews, total = await ReviewService.get_reviews_by_book(
        session, book_id, skip=skip, limit=limit
    )

    return {
        "items": reviews,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 1,
    }


@router.get("/{book_id}/summary", response_model=ReviewSummaryResponse)
async def get_review_summary(
    book_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Get aggregated review summary and rating for a book.

    Args:
        book_id: Book ID
        session: Database session

    Returns:
        Review summary with aggregated rating

    Raises:
        HTTPException: If book not found
    """
    try:
        # Check if book exists
        book = await BookService.get_book_by_id(session, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        # Get review statistics
        avg_rating, total_reviews = await ReviewService.get_book_rating_summary(
            session, book_id
        )

        # Get review texts for summarization
        reviews, _ = await ReviewService.get_reviews_by_book(
            session, book_id, skip=0, limit=5
        )
        review_texts = [review.review_text for review in reviews]

        # Generate summary if reviews exist
        summary_text = ""
        if review_texts:
            try:
                summary_text = llm_service.generate_review_summary(
                    book.title, review_texts, avg_rating
                )
            except Exception as e:
                logger.warning(f"Could not generate LLM summary: {str(e)}")
                summary_text = f"Book has {total_reviews} reviews with an average rating of {avg_rating}/5."
        else:
            summary_text = "No reviews available for this book yet."

        return ReviewSummaryResponse(
            book_id=book_id,
            book_title=book.title,
            total_reviews=total_reviews,
            average_rating=avg_rating,
            summary=summary_text,
            generated_at=datetime.utcnow(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting review summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating review summary"
        ) from e


@router.put("/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    session: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Update a review.

    Args:
        review_id: Review ID
        review_data: Review update data
        session: Database session
        user_id: Current user ID

    Returns:
        Updated review information

    Raises:
        HTTPException: If review not found or user is not the author
    """
    try:
        # Check if review exists and user is the author
        review = await ReviewService.get_review_by_id(session, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reviews"
            )

        updated_review = await ReviewService.update_review(session, review_id, review_data)
        logger.info(f"Review updated: {review_id}")
        return updated_review
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) from e


@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    session: AsyncSession = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete a review.

    Args:
        review_id: Review ID
        session: Database session
        user_id: Current user ID

    Raises:
        HTTPException: If review not found or user is not the author
    """
    try:
        # Check if review exists and user is the author
        review = await ReviewService.get_review_by_id(session, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        if review.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews"
            )

        success = await ReviewService.delete_review(session, review_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
            )

        logger.info(f"Review deleted: {review_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting review"
        ) from e
