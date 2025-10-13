# Truth Net Server

FastAPI-based backend for the Truth Net verified knowledge platform.

## Quick Start

### 1. Prerequisites
- Python 3.11+
- Poetry
- Docker & Docker Compose

### 2. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and set required values (especially JWT_SECRET for production)
# Generate secure JWT secret:
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

### 3. Install Dependencies
```bash
poetry install
```

### 4. Start Services
```bash
# PostgreSQL, Redis, MeiliSearch
docker compose up -d
```

### 5. Run Database Migrations
```bash
# Apply all migrations
poetry run alembic upgrade head

# Or generate new migration after model changes
poetry run alembic revision --autogenerate -m "Description"
```

### 6. Start Development Server
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:
- **API:** http://localhost:8000
- **Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health

## Environment Variables
All configuration is managed through `.env` and `app/config.py`. 

**Critical Settings:**
- `TRUTHNET_JWT_SECRET` - Must be changed for production (32+ characters)
- `TRUTHNET_ENVIRONMENT` - Set to `production` for production deployment
- `TRUTHNET_ALLOW_ORIGINS` - Comma-separated CORS origins
- `TRUTHNET_DATABASE_URL` - PostgreSQL connection string

See `.env.example` for the complete list with descriptions.

## Directory Layout
- `app/`
  - `auth/`: Authentication helpers, password hashing, JWT issuance.
  - `models/`: SQLAlchemy models for members, sites, pages, social features.
  - `routes/`: FastAPI routers grouped by domain.
  - `schemas/`: Pydantic models mirroring API shapes.
  - `services/`: Domain services (search, moderation, social feed, ingestion).
  - `tasks/`: Celery/RQ workers for async pipelines.
- `scripts/`: CLI tooling for admin setup, demo content loading, data maintenance.

## Demo Content
Triplet of sample sites lives in `../docs/demo-content/`. Use `scripts/load_demo_content.py` to seed the database for demos:

```bash
poetry run python scripts/load_demo_content.py
```

## Security Features

### Authentication & Authorization
- **JWT-based authentication** with access and refresh tokens
- **Token type validation** prevents refresh token misuse
- **Role-based access control (RBAC)** for protected endpoints
- **Password complexity requirements** (8+ chars, upper, lower, digit)

### Rate Limiting
- Redis-backed rate limiting (60 req/min default)
- Stricter limits for auth endpoints (10 req/min)
- Per-endpoint and global per-IP limits
- Method-aware rate limiting

### Security Headers
- Content Security Policy (CSP)
- X-Frame-Options (clickjacking protection)
- X-Content-Type-Options (MIME sniffing protection)
- Strict-Transport-Security (HSTS) in production
- Referrer-Policy and Permissions-Policy

### Data Integrity
- Unique constraints on critical relationships
- Foreign key constraints for referential integrity
- Indexes for query performance
- See migration `002_add_constraints_and_indexes.py`

## API Endpoints

### Authentication (`/v1/auth`)
- `POST /signup` - Register new user
- `POST /login` - Login with email/username
- `GET /me` - Get current user profile

### Sites (`/v1/sites`)
- Site management and publishing
- Page content and versioning

### Social (`/v1/social`)
- Truth posts and threads
- Comments and reactions
- Social insights and trending content

### Search (`/v1/search`)
- Full-text search across sites and pages
- MeiliSearch-powered with DB fallback

### Moderation (`/v1/moderation`) 🔒 *Requires curator/admin role*
- Submission queue management
- Review workflows

### Fact Checking (`/v1/fact-check`) 🔒 *Requires authentication*
- Dual-layer fact checking runs
- Evidence evaluation

### Health Endpoints
- `GET /health` - Basic health check
- `GET /healthz` - Kubernetes liveness probe
- `GET /readyz` - Kubernetes readiness probe (checks DB, search)
- `GET /metrics` - Prometheus metrics

## Production Deployment

### Pre-deployment Checklist
- [ ] Set `TRUTHNET_ENVIRONMENT=production`
- [ ] Generate and set secure `TRUTHNET_JWT_SECRET`
- [ ] Configure `TRUTHNET_ALLOW_ORIGINS` with actual frontend URLs
- [ ] Configure `TRUTHNET_ALLOWED_HOSTS` with actual domains
- [ ] Use strong database credentials
- [ ] Enable Redis authentication
- [ ] Set MeiliSearch API key
- [ ] Run database migrations
- [ ] Configure HTTPS/TLS
- [ ] Set up monitoring and logging

### Running in Production

```bash
# Use production ASGI server (e.g., Gunicorn with Uvicorn workers)
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### Docker Deployment

```bash
# Build production image
docker build -t truthnet-server:latest .

# Run with environment file
docker run -d \
  --name truthnet-server \
  --env-file .env.production \
  -p 8000:8000 \
  truthnet-server:latest
```

## Monitoring & Observability

### Logging
- Structured logging with request IDs
- All requests logged with method, path, status, duration
- Set `X-Request-ID` header in responses

### Metrics
- Prometheus-compatible `/metrics` endpoint
- Application uptime and version info
- Recommended: Add `prometheus_fastapi_instrumentator` for full metrics

### Health Checks
- `/health` - Always returns OK if server running
- `/readyz` - Checks database and search service connectivity
- Use `/readyz` for Kubernetes readiness probes

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test file
poetry run pytest tests/test_fact_check.py -v
```

## Development

### Database Migrations
```bash
# Generate migration after model changes
poetry run alembic revision --autogenerate -m "Add new field"

# Apply migrations
poetry run alembic upgrade head

# Rollback one migration
poetry run alembic downgrade -1

# Show migration history
poetry run alembic history
```

### Code Quality
```bash
# Format code
poetry run black app/

# Lint
poetry run ruff check app/

# Type checking
poetry run mypy app/
```

## Troubleshooting

### Database Connection Issues
- Check PostgreSQL is running: `docker compose ps`
- Verify connection string in `.env`
- Check migrations applied: `poetry run alembic current`

### Rate Limiting Not Working
- Verify Redis is running: `docker compose ps`
- Check Redis connection: `redis-cli ping`
- Review logs for rate limit middleware errors

### Authentication Errors
- Ensure JWT secret is set and consistent
- Check token expiry settings
- Verify user roles in database

## Additional Documentation

- **Security Assessment Report:** See `../SECURITY_FIXES.md`
- **API Documentation:** Visit `/docs` when server is running
- **Architecture:** See `../docs/architecture.md`
