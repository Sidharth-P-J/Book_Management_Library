# Deployment Guide

This guide provides step-by-step instructions for deploying the Book Management System to various environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [AWS Deployment](#aws-deployment)
4. [Database Setup](#database-setup)
5. [Environment Configuration](#environment-configuration)
6. [Health Checks and Monitoring](#health-checks-and-monitoring)

## Local Development

### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd book-management-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create PostgreSQL database**
   ```bash
   createdb -U postgres book_management
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your settings:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/book_management
   DATABASE_SYNC_URL=postgresql://postgres:password@localhost:5432/book_management
   SECRET_KEY=your-secret-key-min-32-chars
   GROQ_API_KEY=your-groq-api-key
   DEBUG=True
   ```

6. **Initialize database**
   ```bash
   python -c "
   import asyncio
   from src.core import init_db
   asyncio.run(init_db())
   "
   ```

7. **Run application**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/api/docs
   - ReDoc: http://localhost:8000/api/redoc

## Docker Deployment

### Prerequisites
- Docker
- Docker Compose

### Quick Start

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd book-management-system
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   ```

   Update required variables in `.env`:
   ```env
   GROQ_API_KEY=your-groq-api-key
   SECRET_KEY=your-secret-key-min-32-chars
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   docker-compose logs -f api
   curl http://localhost:8000/health
   ```

5. **Stop services**
   ```bash
   docker-compose down
   ```

### Docker Compose Services

- **PostgreSQL** (Port 5432): Database
- **FastAPI** (Port 8000): Application server

### Building Custom Images

1. **Build image**
   ```bash
   docker build -t book-management-api:latest .
   ```

2. **Run container**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e DATABASE_URL="postgresql+asyncpg://postgres:password@db:5432/book_management" \
     -e GROQ_API_KEY="your-api-key" \
     --name book_api \
     book-management-api:latest
   ```

## AWS Deployment

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│         CloudFront (CDN)                     │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│    Application Load Balancer (ALB)           │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│  ECS Fargate (Container Orchestration)       │
│  - Multiple Task Instances                   │
│  - Auto-scaling                              │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
┌───────▼────────┐   ┌────────▼─────────┐
│   RDS Aurora   │   │ ElastiCache Redis │
│   (PostgreSQL) │   │ (Optional)        │
└────────────────┘   └───────────────────┘
```

### Step 1: Create RDS Database

1. **Go to AWS RDS Console**
2. **Create Database**
   - Engine: PostgreSQL 15
   - DB instance class: db.t3.micro (free tier eligible)
   - Allocated storage: 20 GB
   - DB name: book_management
   - Master username: postgres
   - Auto backup: 7 days

3. **Note the endpoint**: `book-db.xxxxx.rds.amazonaws.com`

### Step 2: Create ECR Repository

1. **Create repository**
   ```bash
   aws ecr create-repository --repository-name book-management-api
   ```

2. **Get login command**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
   ```

3. **Build and push image**
   ```bash
   docker build -t book-management-api:latest .
   docker tag book-management-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/book-management-api:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/book-management-api:latest
   ```

### Step 3: Create ECS Cluster

1. **Create cluster**
   ```bash
   aws ecs create-cluster --cluster-name book-management-cluster
   ```

2. **Create task definition** (`task-definition.json`):
   ```json
   {
     "family": "book-management-api",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "containerDefinitions": [
       {
         "name": "book-management-api",
         "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/book-management-api:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "DATABASE_URL",
             "value": "postgresql+asyncpg://postgres:password@book-db.xxxxx.rds.amazonaws.com:5432/book_management"
           },
           {
             "name": "SECRET_KEY",
             "value": "your-secret-key"
           },
           {
             "name": "GROQ_API_KEY",
             "value": "your-groq-api-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/book-management-api",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

3. **Register task definition**
   ```bash
   aws ecs register-task-definition --cli-input-json file://task-definition.json
   ```

### Step 4: Create Service

1. **Create Application Load Balancer**
   ```bash
   aws elbv2 create-load-balancer \
     --name book-management-alb \
     --subnets subnet-xxxxx subnet-yyyyy \
     --security-groups sg-xxxxx
   ```

2. **Create target group**
   ```bash
   aws elbv2 create-target-group \
     --name book-management-targets \
     --protocol HTTP \
     --port 8000 \
     --vpc-id vpc-xxxxx \
     --target-type ip
   ```

3. **Create ECS service**
   ```bash
   aws ecs create-service \
     --cluster book-management-cluster \
     --service-name book-management-api \
     --task-definition book-management-api \
     --desired-count 2 \
     --launch-type FARGATE \
     --load-balancers targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=book-management-api,containerPort=8000 \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx]}"
   ```

### Step 5: Configure Auto-Scaling

```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/book-management-cluster/book-management-api \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --policy-name book-management-scaling \
  --service-namespace ecs \
  --resource-id service/book-management-cluster/book-management-api \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
  "TargetValue=70.0,PredefinedMetricSpecification={PredefinedMetricType=ECSServiceAverageCPUUtilization}"
```

## Database Setup

### PostgreSQL Configuration

1. **Create database user**
   ```sql
   CREATE USER book_user WITH PASSWORD 'secure_password';
   CREATE DATABASE book_management OWNER book_user;
   ```

2. **Enable required extensions**
   ```sql
   \c book_management
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```

3. **Create tables** (automatic with application startup)
   ```bash
   python -c "import asyncio; from src.core import init_db; asyncio.run(init_db())"
   ```

### Backup Strategy

1. **Automated backups** (RDS)
   - Retention: 7-35 days
   - Backup window: 03:00-04:00 UTC

2. **Manual backup**
   ```bash
   pg_dump -U postgres -h localhost -d book_management > backup.sql
   ```

3. **Restore backup**
   ```bash
   psql -U postgres -h localhost -d book_management < backup.sql
   ```

## Environment Configuration

### Production Environment

```env
# Application
DEBUG=False
API_TITLE="Book Management System API"
API_VERSION="1.0.0"

# Database (RDS)
DATABASE_URL=postgresql+asyncpg://user:password@rds-endpoint:5432/book_management
DATABASE_SYNC_URL=postgresql://user:password@rds-endpoint:5432/book_management
DATABASE_ECHO=False

# JWT
SECRET_KEY=generate-strong-random-string-at-least-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# LLM (Groq)
GROQ_API_KEY=your-production-groq-key
LLM_MODEL=mixtral-8x7b-32768
MAX_TOKENS=1024

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Security
SECURE_COOKIES=True
SAME_SITE=Strict
```

### Using AWS Secrets Manager

```bash
aws secretsmanager create-secret \
  --name book-management/prod \
  --secret-string '{
    "DATABASE_URL": "postgresql+asyncpg://...",
    "SECRET_KEY": "...",
    "GROQ_API_KEY": "..."
  }'
```

## Health Checks and Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000/health

# Response:
# {
#   "status": "healthy",
#   "service": "Book Management System API",
#   "version": "1.0.0"
# }
```

### CloudWatch Monitoring

1. **Enable Container Insights**
   ```bash
   aws ecs update-cluster-settings \
     --cluster book-management-cluster \
     --settings name=containerInsights,value=enabled
   ```

2. **Create Alarms**
   ```bash
   aws cloudwatch put-metric-alarm \
     --alarm-name book-api-cpu-high \
     --alarm-description "Alert when API CPU is high" \
     --metric-name CPUUtilization \
     --namespace AWS/ECS \
     --statistic Average \
     --period 300 \
     --threshold 80 \
     --comparison-operator GreaterThanThreshold
   ```

### Logging

1. **CloudWatch Logs**
   - Log Group: `/ecs/book-management-api`
   - Retention: 30 days

2. **Access Logs**
   ```bash
   aws logs tail /ecs/book-management-api --follow
   ```

### Database Monitoring

1. **Enable Performance Insights**
   - Monitor query performance
   - Identify slow queries

2. **Enhanced Monitoring**
   - Set to 1-minute granularity
   - Monitor CPU, memory, I/O

## SSL/TLS Configuration

1. **Request ACM Certificate**
   ```bash
   aws acm request-certificate \
     --domain-name yourdomain.com \
     --validation-method DNS
   ```

2. **Configure ALB with HTTPS**
   ```bash
   aws elbv2 create-listener \
     --load-balancer-arn arn:aws:elasticloadbalancing:... \
     --protocol HTTPS \
     --port 443 \
     --certificates CertificateArn=arn:aws:acm:... \
     --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
   ```

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql -h rds-endpoint -U postgres -d book_management -c "SELECT 1"

# Check security group rules
aws ec2 describe-security-groups --group-ids sg-xxxxx
```

### Application Issues

```bash
# Check logs
docker-compose logs -f api

# Check service health
curl http://localhost:8000/health

# Restart service
docker-compose restart api
```

### Performance Issues

```bash
# Monitor metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --dimensions Name=ClusterName,Value=book-management-cluster \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 300 \
  --statistics Average
```

## Security Checklist

- [ ] Secret key is strong and unique
- [ ] Database password is strong
- [ ] Database is not publicly accessible
- [ ] HTTPS is enabled
- [ ] CORS is properly configured
- [ ] Security groups allow only necessary ports
- [ ] Regular backups are configured
- [ ] Logging is enabled
- [ ] Monitoring and alerts are set up
- [ ] Rate limiting is configured
- [ ] SQL injection prevention is in place
- [ ] CSRF protection is enabled

## Rollback Procedures

### Rolling Back to Previous Version

```bash
# Update ECS service with previous task definition
aws ecs update-service \
  --cluster book-management-cluster \
  --service book-management-api \
  --task-definition book-management-api:1 \
  --force-new-deployment
```

### Database Rollback

```bash
# Stop application
docker-compose down

# Restore backup
psql -U postgres -h localhost < backup.sql

# Restart application
docker-compose up -d
```

## Support

For deployment issues, refer to the README.md and API_DOCUMENTATION.md files.
