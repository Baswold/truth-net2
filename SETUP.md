# Truth Net - Complete Setup Guide

This guide will help you get Truth Net running locally with all optimizations enabled.

## Prerequisites

- **Docker & Docker Compose** (for PostgreSQL, Redis, MeiliSearch, MinIO)
- **Python 3.11+** with Poetry
- **Node.js 18+** with npm
- **Rust** (for Tauri desktop app)

## Quick Start

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd truth-net2

# Create environment file
cd server
cp .env.example .env
```

Edit `.env` with your settings:
```bash
TRUTHNET_ENVIRONMENT=development
TRUTHNET_JWT_SECRET=dev-secret-key-do-not-use-in-production-change-this-immediately
TRUTHNET_DATABASE_URL=postgresql+psycopg://truthnet:truthnet@localhost:5432/truthnet
TRUTHNET_REDIS_URL=redis://localhost:6379/0
TRUTHNET_SEARCH_URL=http://localhost:7700
TRUTHNET_SEARCH_API_KEY=truthnet-dev-key
```

### 2. Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, MeiliSearch, MinIO
docker compose up -d

# Verify services are running
docker compose ps
```

### 3. Setup Backend

```bash
# Install dependencies
poetry install

# Run database migrations
poetry run alembic upgrade head

# Setup MeiliSearch indexes (optional, auto-created on first use)
poetry run python -c "from app.services.search import search_service; search_service.setup_indexes()"

# Load demo content
poetry run python scripts/load_demo_content.py

# Start development server
poetry run uvicorn app.main:app --reload
```

Server will be available at: http://localhost:8000
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/healthz
- Metrics: http://localhost:8000/metrics

### 4. Setup Frontend

```bash
cd ../client

# Install dependencies
npm install

# Generate TypeScript API client
npm run generate-client

# Start desktop app in development
npm run tauri dev
```

## Verification

### Test Backend

```bash
cd server

# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test
poetry run pytest tests/test_fact_check.py -v
```

Expected output: All tests pass ✅

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/healthz

# Readiness check (verifies DB + MeiliSearch)
curl http://localhost:8000/readyz

# Search (database fallback if MeiliSearch not ready)
curl "http://localhost:8000/v1/search?q=truth&limit=5"

# Sites list with pagination
curl "http://localhost:8000/v1/sites?limit=10&offset=0"
```

### Test Authentication

```bash
# Signup
curl -X POST http://localhost:8000/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "display_name": "Test User",
    "password": "securepassword123"
  }'

# Login
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_username": "testuser",
    "password": "securepassword123"
  }'

# Get current user (requires auth token from login)
curl http://localhost:8000/v1/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Test Rate Limiting

```bash
# Send 65 requests rapidly (limit is 60/minute)
for i in {1..65}; do 
  curl -s -w "\nStatus: %{http_code}\n" http://localhost:8000/v1/sites | grep -E "(Status:|Retry-After)"
done
```

Expected: First 60 succeed (200), remaining get 429 with `Retry-After` header.

## Development Workflow

### Backend Development

```bash
cd server

# Auto-reload on code changes
poetry run uvicorn app.main:app --reload

# Create new migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback migration
poetry run alembic downgrade -1

# Format code
poetry run black .

# Lint
poetry run ruff check .
```

### Frontend Development

```bash
cd client

# Regenerate API client after backend changes
npm run generate-client

# Run linter
npm run lint

# Development mode (hot reload)
npm run dev
```

### Database Management

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U truthnet

# View all sites
SELECT id, slug, title, status FROM site;

# Check indexes
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename IN ('site', 'page', 'truth_post');
```

### Redis Management

```bash
# Connect to Redis
docker compose exec redis redis-cli

# View rate limit keys
KEYS rate_limit:*

# Check a specific key's value and TTL
GET rate_limit:127.0.0.1:/v1/sites
TTL rate_limit:127.0.0.1:/v1/sites
```

### MeiliSearch Management

```bash
# Check indexes
curl http://localhost:7700/indexes \
  -H "Authorization: Bearer truthnet-dev-key"

# Search directly in MeiliSearch
curl -X POST http://localhost:7700/indexes/sites/search \
  -H "Authorization: Bearer truthnet-dev-key" \
  -H "Content-Type: application/json" \
  -d '{"q": "truth", "limit": 5}'
```

## Production Deployment

### Environment Setup

```bash
# Generate secure JWT secret
python -c 'import secrets; print(secrets.token_urlsafe(32))'

# Set production environment variables
export TRUTHNET_ENVIRONMENT=production
export TRUTHNET_JWT_SECRET=<generated-secret>
export TRUTHNET_DATABASE_URL=postgresql://user:pass@host:5432/db
export TRUTHNET_REDIS_URL=redis://host:6379/0
export TRUTHNET_SEARCH_URL=https://meilisearch-host:7700
export TRUTHNET_SEARCH_API_KEY=<production-key>
```

### Deploy Backend

```bash
cd server

# Install dependencies
poetry install --only main

# Run migrations
poetry run alembic upgrade head

# Start with production settings
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Build Desktop App

```bash
cd client

# Install dependencies
npm ci

# Generate API client
npm run generate-client

# Build for all platforms
npm run tauri build

# Or build for specific platform
npm run tauri build -- --target x86_64-apple-darwin  # macOS Intel
npm run tauri build -- --target aarch64-apple-darwin # macOS ARM
npm run tauri build -- --target x86_64-pc-windows-msvc # Windows
```

### Docker Deployment (Production)

```yaml
# docker-compose.prod.yml
services:
  api:
    build: ./server
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      TRUTHNET_ENVIRONMENT: production
      TRUTHNET_JWT_SECRET: ${JWT_SECRET}
      TRUTHNET_DATABASE_URL: ${DATABASE_URL}
      TRUTHNET_REDIS_URL: redis://redis:6379/0
      TRUTHNET_SEARCH_URL: http://meilisearch:7700
    depends_on:
      - postgres
      - redis
      - meilisearch
    ports:
      - "8000:8000"

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: truthnet
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis-data:/data

  meilisearch:
    image: getmeili/meilisearch:v1.9
    environment:
      MEILI_MASTER_KEY: ${MEILI_KEY}
    volumes:
      - meili-data:/meili_data

volumes:
  postgres-data:
  redis-data:
  meili-data:
```

## Monitoring

### Health Checks

```bash
# Kubernetes liveness probe
curl http://localhost:8000/healthz

# Kubernetes readiness probe
curl http://localhost:8000/readyz

# Expected readyz output:
{
  "ready": true,
  "checks": {
    "database": true,
    "search": true
  },
  "details": {
    "database": "Connected",
    "search": "MeiliSearch available"
  }
}
```

### Prometheus Metrics

```bash
curl http://localhost:8000/metrics

# Output (Prometheus format):
# HELP truthnet_uptime_seconds Application uptime in seconds
# TYPE truthnet_uptime_seconds gauge
truthnet_uptime_seconds 123.45

# HELP truthnet_info Application information
# TYPE truthnet_info gauge
truthnet_info{version="0.1.0",environment="development"} 1
```

### Logs

All requests are logged with structured data:
```
2025-10-13 13:12:34 - app.middleware.logging - INFO - Incoming request
  extra={
    "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "method": "GET",
    "path": "/v1/sites",
    "client_ip": "127.0.0.1"
  }

2025-10-13 13:12:34 - app.middleware.logging - INFO - Request completed
  extra={
    "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "status_code": 200,
    "duration_ms": 45.23
  }
```

## Troubleshooting

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker compose ps postgres

# View logs
docker compose logs postgres

# Test connection
poetry run python -c "from app.database import engine; engine.connect(); print('✅ Connected')"
```

### Redis Connection Errors

```bash
# Check if Redis is running
docker compose ps redis

# Test connection
docker compose exec redis redis-cli ping
# Expected: PONG
```

### MeiliSearch Not Working

```bash
# Check if MeiliSearch is running
curl http://localhost:7700/health

# Setup indexes manually
poetry run python -c "from app.services.search import search_service; search_service.setup_indexes()"

# Test database fallback
curl "http://localhost:8000/v1/search?q=test&use_db_fallback=true"
```

### Rate Limiting Issues

```bash
# Check Redis keys
docker compose exec redis redis-cli
> KEYS rate_limit:*
> GET rate_limit:127.0.0.1:/v1/sites

# Clear rate limits for testing
> DEL rate_limit:*
```

### Migration Errors

```bash
# Check current migration
poetry run alembic current

# View migration history
poetry run alembic history

# Rollback and retry
poetry run alembic downgrade -1
poetry run alembic upgrade head
```

## Performance Tuning

### Database Pool

Edit `server/app/config.py`:
```python
db_pool_size: int = 20  # Increase for high traffic
db_max_overflow: int = 40
db_pool_recycle: int = 1800  # Recycle after 30 min
```

### Rate Limiting

Edit `server/app/main.py`:
```python
app.add_middleware(
    RateLimitMiddleware,
    redis_client=redis_client,
    requests_per_minute=120  # Increase limit
)
```

### Caching (Frontend)

Edit `client/src/hooks/useApi.ts`:
```typescript
staleTime: 10 * 60 * 1000,  // Cache for 10 minutes
```

## Support

- **Documentation**: http://localhost:8000/docs (interactive API docs)
- **Health Status**: http://localhost:8000/readyz
- **Logs**: Check console output with request IDs
- **Optimizations**: See `OPTIMIZATIONS.md` for detailed changes
- **Tests**: Run `poetry run pytest` to verify setup
