# API Documentation Guide

## Overview

This document provides comprehensive guidance on using the Book Management System API. The API is built with FastAPI and provides RESTful endpoints for managing books, reviews, users, and AI-powered recommendations.

## Base URL

```
http://localhost:8000
or
http://your-domain.com/api
```

## Authentication

All endpoints (except `/health`) require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer {access_token}
```

## Response Format

All API responses are in JSON format with the following structure:

### Success Response
```json
{
  "data": {},
  "message": "Success",
  "status_code": 200
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Rate Limiting

Currently, there is no rate limiting implemented. For production, consider implementing:
- 100 requests per minute per user
- 1000 requests per day per user

## API Endpoints

### 1. Authentication

#### 1.1 Register User
- **Endpoint**: `POST /auth/register`
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123"
  }
  ```
- **Response**: User object with ID and role
- **Status Codes**: 201 (Created), 400 (Bad Request)

#### 1.2 Login
- **Endpoint**: `POST /auth/login`
- **Authentication**: Not required
- **Request Body**:
  ```json
  {
    "username": "john_doe",
    "password": "SecurePassword123"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer",
    "expires_in": 1800
  }
  ```
- **Status Codes**: 200 (OK), 401 (Unauthorized)

#### 1.3 Get Current User
- **Endpoint**: `GET /auth/me`
- **Authentication**: Required
- **Response**: Current user object
- **Status Codes**: 200 (OK), 401 (Unauthorized)

### 2. Books

#### 2.1 Create Book
- **Endpoint**: `POST /books`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "genre": "Fiction",
    "year_published": 1925,
    "summary": "A classic novel about the American Dream"
  }
  ```
- **Response**: Created book object
- **Status Codes**: 201 (Created), 400 (Bad Request), 401 (Unauthorized)

#### 2.2 Get All Books
- **Endpoint**: `GET /books`
- **Authentication**: Not required
- **Query Parameters**:
  - `skip` (integer, default: 0): Number of records to skip
  - `limit` (integer, default: 10): Number of records to fetch (max: 100)
  - `genre` (string, optional): Filter by genre
  - `author` (string, optional): Filter by author
- **Response**: Paginated list of books
- **Status Codes**: 200 (OK)

#### 2.3 Get Book by ID
- **Endpoint**: `GET /books/{book_id}`
- **Authentication**: Not required
- **Parameters**: `book_id` (integer)
- **Response**: Book object with reviews
- **Status Codes**: 200 (OK), 404 (Not Found)

#### 2.4 Update Book
- **Endpoint**: `PUT /books/{book_id}`
- **Authentication**: Required
- **Parameters**: `book_id` (integer)
- **Request Body** (all fields optional):
  ```json
  {
    "title": "Updated Title",
    "author": "Updated Author",
    "genre": "Updated Genre",
    "year_published": 2023,
    "summary": "Updated summary"
  }
  ```
- **Response**: Updated book object
- **Status Codes**: 200 (OK), 404 (Not Found), 401 (Unauthorized)

#### 2.5 Delete Book
- **Endpoint**: `DELETE /books/{book_id}`
- **Authentication**: Required
- **Parameters**: `book_id` (integer)
- **Response**: Empty (204 No Content)
- **Status Codes**: 204 (No Content), 404 (Not Found), 401 (Unauthorized)

#### 2.6 Search Books
- **Endpoint**: `GET /books/search/{query}`
- **Authentication**: Not required
- **Parameters**: `query` (string)
- **Query Parameters**:
  - `skip` (integer, default: 0)
  - `limit` (integer, default: 10)
- **Response**: Paginated search results
- **Status Codes**: 200 (OK)

### 3. Reviews

#### 3.1 Create Review
- **Endpoint**: `POST /books/{book_id}/reviews`
- **Authentication**: Required
- **Parameters**: `book_id` (integer)
- **Request Body**:
  ```json
  {
    "review_text": "Excellent book! Highly recommended.",
    "rating": 4.5
  }
  ```
- **Response**: Created review object
- **Status Codes**: 201 (Created), 400 (Bad Request), 404 (Book not found), 401 (Unauthorized)

#### 3.2 Get Book Reviews
- **Endpoint**: `GET /books/{book_id}/reviews`
- **Authentication**: Not required
- **Parameters**: `book_id` (integer)
- **Query Parameters**:
  - `skip` (integer, default: 0)
  - `limit` (integer, default: 10)
- **Response**: Paginated list of reviews
- **Status Codes**: 200 (OK), 404 (Book not found)

#### 3.3 Get Review Summary
- **Endpoint**: `GET /books/{book_id}/summary`
- **Authentication**: Not required
- **Parameters**: `book_id` (integer)
- **Response**:
  ```json
  {
    "book_id": 1,
    "book_title": "The Great Gatsby",
    "total_reviews": 5,
    "average_rating": 4.2,
    "summary": "LLM-generated summary of reviews",
    "generated_at": "2024-01-15T10:30:00"
  }
  ```
- **Status Codes**: 200 (OK), 404 (Book not found), 503 (LLM Service Unavailable)

#### 3.4 Update Review
- **Endpoint**: `PUT /books/reviews/{review_id}`
- **Authentication**: Required
- **Parameters**: `review_id` (integer)
- **Request Body** (fields optional):
  ```json
  {
    "review_text": "Updated review text",
    "rating": 5.0
  }
  ```
- **Response**: Updated review object
- **Status Codes**: 200 (OK), 404 (Not Found), 403 (Forbidden), 401 (Unauthorized)

#### 3.5 Delete Review
- **Endpoint**: `DELETE /books/reviews/{review_id}`
- **Authentication**: Required
- **Parameters**: `review_id` (integer)
- **Response**: Empty (204 No Content)
- **Status Codes**: 204 (No Content), 404 (Not Found), 403 (Forbidden), 401 (Unauthorized)

### 4. AI & Recommendations

#### 4.1 Generate Summary
- **Endpoint**: `POST /ai/generate-summary`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "title": "Book Title",
    "author": "Author Name",
    "content": "Long book content or description...",
    "max_tokens": 1024
  }
  ```
- **Response**:
  ```json
  {
    "summary": "Generated summary text",
    "generated_at": "2024-01-15T10:30:00"
  }
  ```
- **Status Codes**: 200 (OK), 503 (LLM Service Unavailable), 401 (Unauthorized)

#### 4.2 Get Recommendations
- **Endpoint**: `POST /ai/recommendations`
- **Authentication**: Required
- **Request Body**:
  ```json
  {
    "user_id": 1,
    "genre": "Fiction",
    "limit": 5,
    "based_on_reviews": false
  }
  ```
- **Response**: List of recommended books
- **Status Codes**: 200 (OK), 500 (Internal Server Error), 401 (Unauthorized)

#### 4.3 Get Recommendations by Genre
- **Endpoint**: `GET /ai/recommendations/genre/{genre}`
- **Authentication**: Required
- **Parameters**: `genre` (string)
- **Query Parameters**:
  - `limit` (integer, default: 5, max: 20)
- **Response**: Recommended books for the genre
- **Status Codes**: 200 (OK), 500 (Error), 401 (Unauthorized)

#### 4.4 Get Popular Books
- **Endpoint**: `GET /ai/recommendations/popular`
- **Authentication**: Required
- **Query Parameters**:
  - `limit` (integer, default: 5, max: 20)
- **Response**: Popular books based on ratings
- **Status Codes**: 200 (OK), 500 (Error), 401 (Unauthorized)

#### 4.5 Get Similar Books
- **Endpoint**: `GET /ai/recommendations/similar/{book_id}`
- **Authentication**: Required
- **Parameters**: `book_id` (integer)
- **Query Parameters**:
  - `limit` (integer, default: 5, max: 20)
- **Response**: Similar books (same genre)
- **Status Codes**: 200 (OK), 404 (Book not found), 500 (Error), 401 (Unauthorized)

## Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful, no content to return |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | LLM service unavailable |

## Error Responses

### Validation Error
```json
{
  "detail": "validation error",
  "errors": [
    {
      "loc": ["body", "rating"],
      "msg": "ensure this value is less than or equal to 5",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### Authentication Error
```json
{
  "detail": "Invalid or expired token",
  "status_code": 401
}
```

### Not Found Error
```json
{
  "detail": "Book not found",
  "status_code": 404
}
```

## Examples

### Example 1: Complete User Flow

1. **Register**
   ```bash
   curl -X POST http://localhost:8000/auth/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john_doe",
       "email": "john@example.com",
       "password": "SecurePassword123"
     }'
   ```

2. **Login**
   ```bash
   curl -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{
       "username": "john_doe",
       "password": "SecurePassword123"
     }'
   ```

3. **Create Book** (using access token from login)
   ```bash
   curl -X POST http://localhost:8000/books \
     -H "Authorization: Bearer {access_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "The Great Gatsby",
       "author": "F. Scott Fitzgerald",
       "genre": "Fiction",
       "year_published": 1925
     }'
   ```

4. **Add Review**
   ```bash
   curl -X POST http://localhost:8000/books/1/reviews \
     -H "Authorization: Bearer {access_token}" \
     -H "Content-Type: application/json" \
     -d '{
       "review_text": "Excellent classic novel!",
       "rating": 5.0
     }'
   ```

5. **Get Recommendations**
   ```bash
   curl -X GET "http://localhost:8000/ai/recommendations/genre/Fiction?limit=5" \
     -H "Authorization: Bearer {access_token}"
   ```

## Field Validation

### User Fields
- **username**: 3-255 characters
- **email**: Valid email format
- **password**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one digit

### Book Fields
- **title**: 1-255 characters
- **author**: 1-255 characters
- **genre**: 1-100 characters
- **year_published**: Valid year
- **summary**: Text (optional)

### Review Fields
- **review_text**: 1-5000 characters
- **rating**: 1-5 (float)

## Performance Tips

1. **Use Pagination**: Always use `skip` and `limit` for large datasets
2. **Filter Results**: Use genre and author filters to reduce data transfer
3. **Cache Recommendations**: Store recommendations locally when possible
4. **Batch Operations**: Combine multiple requests when creating related data
5. **Index Fields**: Frequently searched fields are indexed in the database

## Versioning

Current API Version: 1.0.0

Future changes will maintain backward compatibility through versioning.

## Support

For API support and issues, refer to the main README.md file.
