# Book Management System API

An intelligent book management system using Python, FastAPI, PostgreSQL, and Llama3 generative AI model for generating summaries and recommendations.

## 📚 Table of Contents

- [Quick Navigation](#quick-navigation)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Authentication](#authentication)

## 🚀 Quick Navigation

| Document | Purpose |
|----------|---------|
| **[QUICKSTART.md](QUICKSTART.md)** | Get started in 5 minutes with Docker |
| **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** | Complete API endpoint reference |
| **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** | Production deployment guide |
| **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** | Project overview and technical details |

## ✨ Features

### Core Functionality
- **User Management**: Registration, authentication, and JWT-based authorization
- **Book Management**: CRUD operations for books with filtering and searching
- **Review System**: Create and manage book reviews with ratings
- **AI-Powered Summaries**: Generate book summaries using Llama3 via Groq API
- **Smart Recommendations**: Personalized book recommendations based on:
  - User genre preferences
  - Review history
  - Popularity (ratings)
  - Similar books
- **Review Aggregation**: Automated summaries of reviews using LLM

### Security Features
- JWT-based authentication with access and refresh tokens
- Role-Based Access Control (RBAC) with user roles (admin, user, moderator)
- Password hashing using bcrypt
- Secure API endpoints with Bearer token authentication
- CORS configuration for cross-origin requests

### Database
- PostgreSQL with async SQLAlchemy ORM
- Proper foreign key relationships and constraints
- Cascading deletes for data integrity
- Migration support with Alembic

### Testing
- Comprehensive unit tests for all services
- Integration tests for API endpoints
- Pytest with asyncio support
- Test coverage reporting

### Deployment
- Dockerized application with Docker Compose
- Health check endpoints
- Production-ready configuration
- Cloud-ready architecture

## Architecture

```
book-management-system/
├── src/
│   ├── core/                 # Core configuration and database
│   │   ├── config.py         # Settings management
│   │   ├── database.py       # Database setup
│   │   └── __init__.py
│   ├── models/               # SQLAlchemy ORM models
│   │   └── __init__.py
│   ├── schemas/              # Pydantic request/response schemas
│   │   └── __init__.py
│   ├── services/             # Business logic layer
│   │   ├── user_service.py
│   │   ├── book_service.py
│   │   ├── review_service.py
│   │   ├── recommendation_service.py
│   │   └── __init__.py
│   ├── routes/               # API endpoints
│   │   ├── auth_routes.py
│   │   ├── book_routes.py
│   │   ├── review_routes.py
│   │   ├── recommendation_routes.py
│   │   └── __init__.py
│   ├── auth/                 # Authentication utilities
│   │   └── __init__.py
│   ├── utils/                # Utility modules
│   │   ├── llm.py           # LLM integration
│   │   └── __init__.py
│   ├── main.py              # FastAPI application factory
│   └── __init__.py
├── tests/
│   ├── conftest.py          # Pytest configuration
│   ├── unit/                # Unit tests
│   │   ├── test_user_service.py
│   │   ├── test_book_service.py
│   │   ├── test_review_service.py
│   │   ├── test_auth.py
│   │   └── __init__.py
│   ├── integration/         # Integration tests
│   └── __init__.py
├── alembic/                 # Database migrations
│   ├── versions/
│   ├── env.py
│   ├── script.py.mako
│   └── alembic.ini
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Multi-container setup
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── pytest.ini             # Pytest configuration
└── README.md              # This file
```

## Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Docker and Docker Compose (for containerized deployment)
- Groq API Key (for LLM features)

## Installation

### Local Development Setup

1. **Clone the repository**
   ```bash
   cd c:\Users\aravinthb\Projects\test
   ```

2. **Create a Python virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

5. **Set up PostgreSQL database**
   ```bash
   createdb book_management
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Application
DEBUG=False
API_TITLE="Book Management System API"
API_VERSION="1.0.0"

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/book_management
DATABASE_SYNC_URL=postgresql://postgres:password@localhost:5432/book_management

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM (Groq)
GROQ_API_KEY=your-groq-api-key
LLM_MODEL=llama-3.3-70b-versatile
MAX_TOKENS=1024

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]
```

### Key Configuration Options

- **SECRET_KEY**: Must be at least 32 characters in production
- **GROQ_API_KEY**: Obtain from [Groq Console](https://console.groq.com)
- **LLM_MODEL**: Available models include:
  - llama-3.3-70b-versatile (Recommended)
  - llama-3.1-70b-versatile
  - llama3-70b-8192

## Running the Application

### Option 1: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# The API will be available at http://localhost:8000
# Swagger documentation at http://localhost:8000/api/docs
```

### Option 2: Local Development

1. **Start PostgreSQL**
   ```bash
   # Make sure PostgreSQL is running
   ```

2. **Run the application**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Access the API**
   - API Docs: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc
   - Health Check: http://localhost:8000/health

## API Documentation

### Authentication Endpoints

#### Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Get Current User Profile
```bash
GET /auth/me
Authorization: Bearer {access_token}
```

### Book Endpoints

#### Create Book
```bash
POST /books
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "genre": "Fiction",
  "year_published": 1925,
  "summary": "A classic novel about the American Dream."
}
```

#### Get All Books
```bash
GET /books?skip=0&limit=10&genre=Fiction&author=Fitzgerald
```

#### Get Book by ID
```bash
GET /books/{book_id}
```

#### Update Book
```bash
PUT /books/{book_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "Updated Title",
  "author": "Updated Author"
}
```

#### Delete Book
```bash
DELETE /books/{book_id}
Authorization: Bearer {access_token}
```

#### Search Books
```bash
GET /books/search/{query}?skip=0&limit=10
```

### Review Endpoints

#### Create Review
```bash
POST /books/{book_id}/reviews
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "review_text": "Excellent book! Highly recommended.",
  "rating": 4.5
}
```

#### Get Book Reviews
```bash
GET /books/{book_id}/reviews?skip=0&limit=10
```

#### Get Review Summary
```bash
GET /books/{book_id}/summary
```

#### Update Review
```bash
PUT /books/reviews/{review_id}
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "review_text": "Updated review",
  "rating": 5.0
}
```

#### Delete Review
```bash
DELETE /books/reviews/{review_id}
Authorization: Bearer {access_token}
```

### AI & Recommendation Endpoints

#### Generate Summary
```bash
POST /ai/generate-summary
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "title": "The Great Gatsby",
  "author": "F. Scott Fitzgerald",
  "content": "Long book content or description...",
  "max_tokens": 1024
}
```

#### Get Recommendations
```bash
POST /ai/recommendations
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "user_id": 1,
  "genre": "Fiction",
  "limit": 5,
  "based_on_reviews": false
}
```

#### Get Recommendations by Genre
```bash
GET /ai/recommendations/genre/{genre}?limit=5
Authorization: Bearer {access_token}
```

#### Get Popular Books
```bash
GET /ai/recommendations/popular?limit=5
Authorization: Bearer {access_token}
```

#### Get Similar Books
```bash
GET /ai/recommendations/similar/{book_id}?limit=5
Authorization: Bearer {access_token}
```

## Testing

### Run All Tests
```bash
pytest
```

### Run Tests with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/unit/test_user_service.py
```

### Run Specific Test
```bash
pytest tests/unit/test_user_service.py::test_create_user
```

### Test Files

- `tests/unit/test_user_service.py` - User service tests
- `tests/unit/test_book_service.py` - Book service tests
- `tests/unit/test_review_service.py` - Review service tests
- `tests/unit/test_auth.py` - Authentication tests

## Deployment

### Docker Deployment

1. **Build the Docker image**
   ```bash
   docker build -t book-management-api:latest .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Check logs**
   ```bash
   docker-compose logs -f api
   ```

### Production Considerations

1. **Environment Variables**: Use strong secret keys and secure API keys
2. **Database**: Use managed PostgreSQL service (AWS RDS, Azure Database, etc.)
3. **LLM Service**: Ensure Groq API key is securely stored
4. **HTTPS**: Configure SSL/TLS certificates
5. **Monitoring**: Set up application monitoring and logging
6. **Backups**: Configure automated database backups
7. **Scaling**: Use load balancers for multiple instances

### AWS Deployment

1. **RDS Database**
   - Create PostgreSQL RDS instance
   - Update DATABASE_URL with RDS endpoint

2. **ECS/Fargate**
   - Push Docker image to ECR
   - Create ECS task definition
   - Configure security groups and load balancer

3. **Environment Management**
   - Store secrets in AWS Secrets Manager
   - Use IAM roles for permissions

## Authentication

### JWT Tokens

The API uses JWT (JSON Web Tokens) for authentication:

- **Access Token**: Valid for 30 minutes (configurable)
- **Refresh Token**: Valid for 7 days (configurable)

### Using Tokens

Include the access token in the `Authorization` header:

```bash
Authorization: Bearer {access_token}
```

### Token Structure

Tokens contain the following claims:
- `sub`: User ID
- `username`: Username
- `role`: User role (admin, user, moderator)
- `type`: Token type (access, refresh)
- `exp`: Expiration time

## Development

### Adding New Endpoints

1. Create schema in `src/schemas/__init__.py`
2. Create service method in `src/services/`
3. Create route in `src/routes/`
4. Add unit tests in `tests/unit/`
5. Update API documentation

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
psql -U postgres -d book_management -c "SELECT 1"

# Update DATABASE_URL in .env
```

### LLM Service Not Working

```bash
# Verify Groq API key
# Check GROQ_API_KEY environment variable
# Review logs for specific error messages
```

### Port Already in Use

```bash
# Change port in docker-compose.yml or uvicorn command
uvicorn src.main:app --port 8001
```

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please refer to the API documentation at `/api/docs`.

## Performance Considerations

### Database
- Indexes on frequently queried fields (title, author, user_id)
- Connection pooling with asyncpg
- Pagination for large result sets

### Caching
- Recommendations can be cached using Redis (optional)
- Review summaries can be cached

### Async Operations
- All database operations are asynchronous
- Non-blocking I/O for API requests
- Efficient resource utilization

## Future Enhancements

- [ ] Redis caching layer for recommendations
- [ ] Elasticsearch for full-text search
- [ ] WebSocket support for real-time updates
- [ ] File upload for book covers
- [ ] Advanced recommendation algorithms
- [ ] User following and social features
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] Rate limiting
- [ ] GraphQL API
