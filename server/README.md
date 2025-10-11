# Truth Net Server

## Quick Start
1. Copy `.env.example` to `.env` and adjust secrets.
2. Install dependencies via Poetry:
   ```bash
   poetry install
   ```
3. Launch services with Docker Compose (PostgreSQL, Redis, MeiliSearch, MinIO):
   ```bash
   docker compose up -d
   ```
4. Run database migrations (coming soon) and start the API:
   ```bash
   poetry run uvicorn app.main:app --reload
   ```

## Environment Variables
All configuration is managed through `.env` and `app/config.py`. See `.env.example` for the canonical list.

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
Triplet of sample sites lives in `../docs/demo-content/`. Use the forthcoming `scripts/load_demo_content.py` to seed the database for demos.
