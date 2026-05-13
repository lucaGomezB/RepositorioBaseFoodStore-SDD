# Design: setup-backend-config

## Context

The monorepo has been scaffolded (setup-monorepo-base) with:
- Empty `backend/app/` directory with placeholder files
- Empty `backend/app/core/`, `backend/app/modules/`
- No FastAPI application instance
- No database configuration

This change configures the foundational backend infrastructure needed for all subsequent backend changes.

## Goals / Non-Goals

**Goals:**
- Create a working FastAPI application instance with CORS middleware
- Configure SQLAlchemy with connection string from environment
- Set up dependency injection for database sessions
- Create a health check endpoint
- Have `uvicorn app.main:app --reload` work successfully

**Non-Goals:**
- Database migrations (handled in setup-database-seed)
- Authentication/authorization (handled in auth-* changes)
- API routes beyond health check (handled in feature modules)

## Decisions

### 1. FastAPI with Uvicorn
**Decision**: Use FastAPI as the web framework with Uvicorn as the ASGI server.
**Rationale**: FastAPI provides automatic OpenAPI docs, type validation, and async support. It's required by the project spec.
**Alternative considered**: Flask — less modern, no async native support.

### 2. SQLAlchemy over raw psycopg2
**Decision**: Use SQLAlchemy 2.0 with async support pattern (sync for simplicity initially).
**Rationale**: Provides ORM, migrations support (Alembic), and abstraction over database engine. Required by project.
**Alternative considered**: Raw SQL with psycopg2 — too verbose, harder to maintain.

### 3. Environment-based configuration
**Decision**: All config via environment variables, loaded from `.env`.
**Rationale**: Security best practice, no hardcoded credentials, 12-factor app compliance.
**Alternative considered**: config file — rejected as credentials would be in repo.

### 4. CORS for localhost development
**Decision**: Configure CORS to allow http://localhost:5173 (frontend dev server).
**Rationale**: Frontend runs on different port during development. Will be configurable via env.
**Alternative considered**: No CORS — blocks frontend development.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-------------|
| Database not available | App fails to start | Create startup check, clear error message |
| Missing .env | No config values | Provide .env.example, fail fast with helpful error |
| CORS too permissive | Security concern | Restrict to known origins via env var |

## Migration Plan

1. Create/update `backend/requirements.txt` with dependencies
2. Copy `.env.example` to `.env` and configure DATABASE_URL
3. Run `python -m app.main` to verify app starts
4. Verify health endpoint at `http://localhost:8000/health`
5. Verify Swagger UI at `http://localhost:8000/docs`

## Open Questions

- Should we use async SQLAlchemy (asyncpg) from the start, or start sync and migrate later?
  - **Current decision**: Start with sync for simplicity, migrate to async in a later change if needed
- Should Alembic be configured here or in setup-database-seed?
  - **Current decision**: setup-database-seed — keep this change focused on app config only