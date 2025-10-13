# Changelog

All notable optimizations and improvements to Truth Net.

## [0.1.0] - 2025-10-13

### 🔒 Security

- **JWT Authentication**: Implemented proper Bearer token auth with `get_current_user` dependency
- **Fixed /auth/me endpoint**: Now requires valid JWT token instead of returning first user
- **Secure secrets**: Enforced 32+ character JWT secret, validates against dev defaults in production
- **Rate limiting**: Redis-backed sliding window rate limiter (60 req/min per IP)
- **Environment validation**: Fails fast on insecure production configurations

### ⚡ Performance

- **Eliminated N+1 queries**: Search endpoint uses `joinedload(Page.site)` for eager loading
- **Pagination everywhere**: All list endpoints support `limit`/`offset` with sensible defaults
- **Database indexes**: 15+ indexes on status, timestamps, and JSONB fields via Alembic migration
- **Connection pooling**: Configurable pool sizes with automatic recycling and pre-ping
- **MeiliSearch integration**: Full-text search with highlighting, graceful DB fallback
- **Query optimization**: Composite indexes for polymorphic lookups, GIN indexes for JSONB

### 🎯 API Improvements

- **Pydantic v2**: All models use `ConfigDict` instead of deprecated inner `Config` class
- **OpenAPI client**: Auto-generated TypeScript client with axios integration
- **Consistent pagination**: `limit` (max 100), `offset` (default 0) across all endpoints
- **Filter support**: Status, type, and other filters on list endpoints
- **Enhanced search**: Type filters, highlighting, MeiliSearch integration with fallback

### 📊 Observability

- **Structured logging**: Request IDs, timing, context in every log entry
- **Health endpoints**: `/healthz` (liveness), `/readyz` (readiness), `/metrics` (Prometheus)
- **Request tracking**: X-Request-ID header on all responses
- **Rate limit headers**: X-RateLimit-Limit, X-RateLimit-Remaining, Retry-After
- **Dependency checks**: Readiness probe validates DB and MeiliSearch connectivity

### 🗄️ Database

- **Initial migration**: Complete schema with all tables via Alembic
- **Unique constraints**: `(site_id, path)` on pages, `(follower_id, following_id)` on follows
- **Performance indexes**: 15+ indexes on frequently queried columns
- **GIN indexes**: Full-text search on JSONB columns (tags, metadata)
- **Environment-driven**: Alembic uses `settings.database_url` instead of hardcoded INI value

### 🐛 Bug Fixes

- **Demo loader**: Fixed `page_metadata=` attribute mismatch (was `metadata=`)
- **Timestamps**: Consistent `published_at` across pages and content versions
- **JWT secret**: Default now meets 32-character minimum requirement
- **Version commits**: Proper flush before setting `live_version_id` on pages

### 🎨 Frontend

- **API client**: Generated TypeScript client from OpenAPI spec
- **React Query hooks**: Pre-configured hooks for all major endpoints with caching
- **Auth flow**: Auto token injection, refresh handling, error interception
- **Stale times**: Intelligent cache durations (5 min sites, 2 min search)
- **Optimistic updates**: Mutations invalidate related queries automatically

### 📦 Dependencies

**Organized by category:**
- Core: FastAPI, Pydantic, Uvicorn
- Database: SQLAlchemy, Psycopg, Alembic
- Auth: Passlib, Bcrypt, Python-JOSE
- Caching: Redis
- Search: MeiliSearch
- Background jobs: Celery, Croniter, Arrow (reserved for future)
- Utilities: httpx, python-multipart, pyyaml (partially reserved)

### 📝 Documentation

- **OPTIMIZATIONS.md**: Comprehensive list of all improvements with metrics
- **SETUP.md**: Step-by-step setup guide with troubleshooting
- **client/README.md**: Frontend setup, client generation, build instructions
- **Inline comments**: Dependency purpose documented in `pyproject.toml`

### 🧪 Testing

- All existing tests pass with new optimizations
- Schema validated via test suite
- Pagination tested across endpoints
- Pydantic v2 compatibility verified

### 🚀 Deployment

- Health checks ready for Kubernetes
- Prometheus metrics endpoint
- Environment-driven configuration
- Migration rollback support
- Multi-platform build targets documented

## Migration Guide

### From Previous Version

1. **Update environment variables:**
   ```bash
   export TRUTHNET_JWT_SECRET=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')
   ```

2. **Run migrations:**
   ```bash
   poetry run alembic upgrade head
   ```

3. **Setup MeiliSearch indexes:**
   ```bash
   poetry run python -c "from app.services.search import search_service; search_service.setup_indexes()"
   ```

4. **Update frontend:**
   ```bash
   cd client
   npm install
   npm run generate-client
   ```

### Breaking Changes

- **/auth/me** now requires authentication (use Bearer token)
- **Pagination**: List endpoints now limit results (max 100 per request)
- **Pydantic**: Models use `ConfigDict` (internal change, no API impact)

### Deprecations

- None in this release

## Performance Benchmarks

### Expected Improvements

- **Search**: 10-100x faster with MeiliSearch vs SQL ILIKE
- **N+1 queries**: 50%+ reduction in query count for search endpoint
- **Indexes**: 10-100x faster filters on status/timestamps/tags
- **Caching**: 80%+ reduction in redundant API calls (React Query)
- **Connection pooling**: Eliminates handshake overhead, reuses connections

## Security Advisories

- **JWT Secret**: Change default secret before deploying to production
- **Rate Limiting**: Configure limits based on expected traffic
- **CORS**: Update `allow_origins` to match your deployment domains

## Next Steps

Planned for v0.2.0:
- [ ] Celery background jobs for content ingestion
- [ ] Token refresh endpoint (`/v1/auth/refresh`)
- [ ] File upload support for site builder
- [ ] Prometheus integration (`prometheus_fastapi_instrumentator`)
- [ ] Email verification and password reset
- [ ] Enhanced search filters and facets
- [ ] WebSocket support for live collaboration

## Contributors

Thanks to everyone who contributed to these optimizations!

---

**Full Changelog**: https://github.com/truthnet/platform/compare/v0.0.1...v0.1.0
