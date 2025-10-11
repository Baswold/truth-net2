# Truth Net Platform Architecture

## Overview
The Truth Net platform consists of three major pieces:

1. A centralized backend that stores curated "truthful" content, orchestrates moderation, and exposes APIs.
2. A content creation and ingestion toolset for members/curators to add new material or import vetted external pages.
3. A cross-platform desktop client that behaves like a dedicated browser for the curated network.

All traffic between clients and the backend is encrypted and authenticated. Only registered members with issued credentials can access the network.

## High-Level Components

```mermaid
graph TD
    subgraph Server
        API[FastAPI REST & WebSocket API]
        Admin[Moderation Dashboard]
        Builder[Site Builder UI]
        Ingest[Ingestion Pipeline]
        DB[(PostgreSQL)]
        Search[(MeiliSearch)]
        Cache[(Redis)]
        Storage[(Object Storage / S3 compatible)]
    end

    subgraph Desktop Client (Tauri)
        Shell[Shell UI / Navigation]
        Renderer[Content Renderer]
        Settings[Feature Toggles]
        Notifications[Notifications]
        BuilderEmbed[Embedded Site Builder]
        OfflineCache[(IndexedDB / SQLite)]
    end

    API <--> DB
    API <--> Cache
    API <--> Search
    API <--> Storage
    API <--> Desktop Client (Tauri)
    BuilderEmbed --> Builder
    Notifications --> API
    Ingest --> Storage
    Ingest --> DB
    Admin --> API
```

## Backend (FastAPI) Modules

- **`app/main.py`**: FastAPI entrypoint, router registration, CORS, middleware.
- **`app/config.py`**: Typed settings (Pydantic) for secrets, database URLs, feature toggles.
- **`app/auth/`**: JWT issuance, refresh tokens, WebAuthn registration, role-based access control, audit logging of sessions.
- **`app/models/`**: SQLAlchemy ORM models for members, sites, pages, submissions, review actions, truth assertions, content versions, and feature toggles.
- **`app/schemas/`**: Pydantic models for API contracts.
- **`app/services/`**: Business logic modules (moderation service, content service, trust scoring, notification dispatcher, import pipeline orchestrator).
- **`app/routes/`**: Versioned routers (`/v1`) for member management, content browsing, submission workflows, ingestion tasks, and admin functions.
- **`app/websocket/`**: Channels for live collaboration (draft editing, moderation queue updates).
- **`site_builder/`**: Embedded React frontend compiled as static assets, served by FastAPI; provides WYSIWYG editing, template selection, preview, and publishing actions.
- **`ingestion/`**: Workers for pulling external pages, HTML sanitization, summarization, source extraction, and scheduling periodic revalidation.
- **`scripts/`**: CLI utilities for bootstrapping database, creating the first admin, running migrations (Alembic).

### Data Storage
- **PostgreSQL**: Authoritative relational store. All content (pages/blocks/metadata) and workflow state live here.
- **MeiliSearch**: Optional but recommended fast search index for content discovery.
- **Redis**: Caching, task queues (via RQ or Celery), and WebSocket presence tracking.
- **Object Storage**: Images, documents, media attachments (local S3-compatible service like MinIO in development, actual S3 or Wasabi in production).

### Core Tables (Abbreviated)
- `member`: identity, roles, trust_score, strike_count, public_key.
- `site`: slug, title, description, owner_id, status, feature_flags.
- `page`: site_id, path, status, live_version_id, search_vector.
- `content_version`: page_id, version_number, layout_json, published_at, editor_id.
- `content_block`: version_id, block_index, block_type, block_payload JSONB.
- `submission`: type (new_site, page_update, import), submitted_by, payload, state.
- `review_action`: submission_id, reviewer_id, decision, rationale, penalties.
- `truth_assertion`: page_id, claim_text, verdict, citation.
- `import_source`: submission_id, original_url, snapshot_path, checksum, refresh_interval.
- `feature_toggle`: scope (global/site/member), key, value, updated_by.
- `penalty_ledger`: member_id, penalty_type, amount, resolved_at.

## Desktop Client (Tauri + React)

### Structure
- **`src-tauri/`**: Rust shell handling secure storage, auto-updates, background sync, native menus, and bridging to system notifications.
- **`src/`**: React/TypeScript frontend.
  - `App.tsx`: root router.
  - `pages/`: home feed, site directory, page view, moderation queue, import wizard, settings, profile.
  - `components/`: navigation chrome, content renderer, trust badges, annotation layers.
  - `store/`: Zustand or Redux store for session state, feature toggles, offline cache sync.
  - `services/api.ts`: typed API client (OpenAPI-generated).
  - `features/site-builder/`: embedded builder frame with permission checks.
  - `features/settings/`: toggles for optional features, persisted via API.

### Rendering Flow
1. Client fetches `site` + `page` metadata.
2. Downloads `layout_json` with ordered blocks.
3. React renderer maps each block type to a component (text, image, citation, timeline, etc.).
4. Feature toggles augment rendering (e.g., `enableTrustHeatmap` overlays trust history chart).
5. Content signatures validated before display; mismatches trigger warning modal.

### Offline Support
- IndexedDB (via `idb-keyval`) caches manifests, pages, assets.
- Background sync (Rust side) refreshes data when connectivity resumes.
- Draft submissions stored locally; API sync attempted when online.

## Site Builder Experience
- Powered by TipTap with custom nodes for citation blocks, fact-check callouts, timeline entries, and embeddable media.
- Version control: every save creates `content_version` record; publish selects a version as live.
- Collaboration: WebSocket presence and CRDT-based conflict resolution (Yjs integration).
- Template presets stored as JSON; users can clone and adapt.
- Asset manager integrates with object storage, with automatic alt-text prompting.

## Ingestion Pipeline
1. **Proposal**: Member submits URLs for import with context.
2. **Fetcher**: Downloads HTML, normalizes URLs, removes scripts, captures screenshots.
3. **Analyzer**: Extracts text, generates summary, lists outbound citations, computes similarity hashes for change detection.
4. **Fact Checks**: Curators review summary vs original, add annotations, decide verdict.
5. **Publish**: Approved imports become `page` records with `import_source` metadata and scheduled refresh.
6. **Monitoring**: Cron job re-fetches pages, compares hashes, flags significant changes.

## Moderation & Governance
- Trust score algorithm increments for valuable contributions, decrements for flagged falsehoods.
- Strike system configured in `config.py`; thresholds trigger automatic suspensions.
- Financial penalties recorded in `penalty_ledger`; integration point for external payment processor.
- Audit trail stored in append-only log (e.g., `sqlite` + `hash chain`). Periodic sealed exports for compliance.

## Social Layer
- **`app/models/social.py`**: Contains `TruthPost`, `TruthThread`, `Reaction`, `Follow`, and `CommunityVerdict` models, each tied to trust scoring and moderation metadata.
- **`app/routes/social.py`**: REST + WebSocket endpoints for publishing posts, joining topic hubs, reacting with citations, and surfacing community verdicts.
- **`app/services/social_feed.py`**: Generates ranked feeds blending verified articles, member commentary, and fact-check highlights while respecting feature toggles and trust filters.
- **Client integration**: `client/src/pages/social/` hosts Truth Feed, Topic Hubs, and Member Profiles; feature toggles control visibility of live discussions, annotations, and AI summarizations.
- **Moderation hooks**: Posts and comments pass through automated fact-check queues; strikes propagate across publishing and social privileges.

## Demo Sites & Seed Content
- **`docs/demo-content/`** stores JSON definitions for example sites used in onboarding.
- Initial demo sites:
  1. **Truth Atlas** (`truth-atlas`): Curated encyclopedia with fact-checked articles on science and civics, showcases citation system.
  2. **Civic Pulse** (`civic-pulse`): Daily digest of verified policy updates, featuring timeline blocks and trust heatmaps.
  3. **Health Clarity** (`health-clarity`): Evidence-based health guidance with embedded expert commentary and AI-assisted summaries.
- Seeder script `server/scripts/load_demo_content.py` populates these sites, including sample member profiles and social discussion threads for demo purposes.

## Settings & Feature Toggles
- Feature definitions stored server-side; client fetches on login.
- Toggles cached locally, but enforced server-side (server may deny certain actions if feature disabled).
- Settings UI groups toggles: Reading Experience, Discovery, Moderation Helpers, Safety.

## Deployment
- **Development**: Docker Compose with FastAPI, PostgreSQL, Redis, MeiliSearch, MinIO. Hot reload for API and React-based builder.
- **Production**: Systemd/launchd services on the Mac mini, behind Caddy reverse proxy enforcing mutual TLS. Automatic backups to external storage.
- **CI/CD**: GitHub Actions running tests, linting, building Tauri bundles, pushing Docker images.

## Next Steps
1. Scaffold repository structure (`server/`, `client/`, `docs/`).
2. Initialize FastAPI project with authentication and basic models.
3. Bootstrap PostgreSQL + migrations.
4. Create Tauri React skeleton with secure auth flow.
5. Implement feature toggle settings and minimal browsing experience.
6. Expand builder, ingestion, and moderation workflows iteratively.
