# Quick Start Guide

This guide will help you get the Book Management System API up and running in minutes.

## Prerequisites

- **Python 3.10+**
- **PostgreSQL 12+** OR **Docker & Docker Compose**
- **Git**

## Option 1: Quick Start with Docker (Recommended)

The easiest way to get started is using Docker and Docker Compose.

### Step 1: Clone the Repository

```bash
cd c:\Users\aravinthb\Projects\test
```

### Step 2: Set Up Environment Variables

```bash
copy .env.example .env
```

Edit `.env` and add your Groq API key:

```env
GROQ_API_KEY=your-groq-api-key-here
```

Get your API key from: https://console.groq.com

### Step 3: Start Services

```bash
docker-compose up --build
```

This will:
- Create and start PostgreSQL database
- Build the FastAPI application image
- Start the API server
- Initialize the database

### Step 4: Verify Installation

```bash
curl http://localhost:8000/health
```

You should see:
```json
{
  "status": "healthy",
  "service": "Book Management System API",
  "version": "1.0.0"
}
```

### Step 5: Access the API

- **API Swagger Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **API Base URL**: http://localhost:8000

## Option 2: Local Development Setup

For development with hot reload and local debugging.

### Step 1: Clone Repository

```bash
cd c:\Users\aravinthb\Projects\test
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
source venv/Scripts/activate  # Windows
# or
python -m venv venv && venv\Scripts\activate  # Windows (one-liner)
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up PostgreSQL

**Option A: Using Docker (just the database)**

```bash
docker run -d \
  --name book_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=book_management \
  -p 5432:5432 \
  postgres:15-alpine
```

**Option B: Using Local PostgreSQL**

```bash
createdb -U postgres book_management
```

### Step 5: Configure Environment

```bash
copy .env.example .env
```

Update `.env`:

```env
DEBUG=True
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/book_management
DATABASE_SYNC_URL=postgresql://postgres:postgres@localhost:5432/book_management
GROQ_API_KEY=your-groq-api-key-here
SECRET_KEY=your-secret-key-min-32-chars
```

### Step 6: Initialize Database

```bash
python -c "
import asyncio
from src.core import init_db
asyncio.run(init_db())
"
```

### Step 7: Run Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will start with hot reload enabled.

## First Steps: Test the API

### 1. Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePassword123"
  }'
```

Response:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Save the `access_token` for the next requests.

### 3. Create a Book

```bash
curl -X POST http://localhost:8000/books \
  -H "Authorization: Bearer {YOUR_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "genre": "Fiction",
    "year_published": 1925,
    "summary": "A classic novel about the American Dream"
  }'
```

### 4. Get All Books

```bash
curl http://localhost:8000/books
```

### 5. Add a Review

```bash
curl -X POST http://localhost:8000/books/1/reviews \
  -H "Authorization: Bearer {YOUR_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "review_text": "Excellent classic novel!",
    "rating": 5.0
  }'
```

### 6. Get Book Summary

```bash
curl http://localhost:8000/books/1/summary
```

### 7. Get Recommendations

```bash
curl -X POST http://localhost:8000/ai/recommendations \
  -H "Authorization: Bearer {YOUR_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "genre": "Fiction",
    "limit": 5,
    "based_on_reviews": false
  }'
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Tests

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_user_service.py

# Specific test
pytest tests/unit/test_user_service.py::test_create_user -v
```

## Common Tasks

### Stop Docker Services

```bash
docker-compose down
```

### View Database Logs

```bash
docker-compose logs -f db
```

### View API Logs

```bash
docker-compose logs -f api
```

### Clean Up Everything

```bash
docker-compose down -v
```

This removes containers, networks, and volumes.

### Access PostgreSQL Database

```bash
docker-compose exec db psql -U postgres -d book_management
```

### Reset Database

```bash
docker-compose down -v
docker-compose up -d db
# Wait for database to be ready
docker-compose up api
```

## Using the Swagger UI

1. Go to http://localhost:8000/api/docs
2. Click "Authorize" button
3. Enter your bearer token: `{your_access_token}`
4. Try out endpoints directly in the UI

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # macOS/Linux
netstat -ano | findstr :8000   # Windows (get PID)
taskkill /PID <PID> /F         # Windows (kill)
```

Or run on a different port:

```bash
uvicorn src.main:app --port 8001
```

### Database Connection Error

If you get a database connection error:

```bash
# Check if PostgreSQL is running
# Using Docker:
docker-compose ps

# Using local PostgreSQL:
psql -U postgres -d book_management -c "SELECT 1"
```

### LLM Service Not Working

If LLM features are not working:

1. Check your Groq API key in `.env`
2. Get a new key from https://console.groq.com
3. Restart the application

### Virtual Environment Issues

```bash
# Remove and recreate venv
rm -rf venv
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```

## Next Steps

- Read the [API Documentation](API_DOCUMENTATION.md) for endpoint details
- Check the [Deployment Guide](DEPLOYMENT_GUIDE.md) for production deployment
- Review the [README.md](README.md) for comprehensive documentation

## Architecture Overview

```
┌─────────────────────────────────────────┐
│         FastAPI Application             │
│  ┌─────────────────────────────────┐   │
│  │    Routes (API Endpoints)       │   │
│  │  - /auth                        │   │
│  │  - /books                       │   │
│  │  - /reviews                     │   │
│  │  - /ai (Recommendations)        │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│  ┌────────────▼────────────────────┐   │
│  │     Services (Business Logic)   │   │
│  │  - UserService                  │   │
│  │  - BookService                  │   │
│  │  - ReviewService                │   │
│  │  - RecommendationService        │   │
│  └────────────┬────────────────────┘   │
│               │                         │
│  ┌────────────▼────────────────────┐   │
│  │    Database Models (ORM)        │   │
│  │  - User, Book, Review           │   │
│  └────────────┬────────────────────┘   │
└───────────────┼─────────────────────────┘
                │
    ┌───────────┴────────────┐
    │                        │
┌───▼────────┐      ┌───────▼──────┐
│ PostgreSQL │      │ Groq API     │
│ Database   │      │ (Llama3)     │
└────────────┘      └──────────────┘
```

## File Structure

```
book-management-system/
├── src/
│   ├── core/          # Configuration and database
│   ├── models/        # Database ORM models
│   ├── schemas/       # Pydantic request/response models
│   ├── services/      # Business logic
│   ├── routes/        # API endpoints
│   ├── auth/          # Authentication utilities
│   ├── utils/         # LLM and other utilities
│   └── main.py        # FastAPI application
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── conftest.py    # Test configuration
├── docker-compose.yml # Multi-container setup
├── Dockerfile         # Docker image
├── requirements.txt   # Python dependencies
├── .env.example       # Environment template
└── README.md          # Full documentation
```

## Support

For more help:
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for endpoint details
- Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production setup
- Review source code comments for implementation details

Happy coding! 🚀
