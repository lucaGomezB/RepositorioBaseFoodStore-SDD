# Proposal: setup-backend-config

## Why

The monorepo structure is in place (setup-monorepo-base), but there's no working backend. We need FastAPI configured with SQLAlchemy, core modules, and basic infrastructure before any feature development can start. Without this, the entire backend development is blocked.

## What Changes

1. **FastAPI application setup** — Create `app/main.py` with app instance, title, version, CORS middleware
2. **SQLAlchemy configuration** — Configure database connection in `app/core/database.py` with session management
3. **Core modules placeholders** — Create `app/core/config.py`, `app/core/security.py` with basic structures
4. **Root router setup** — Create `app/api/__init__.py` with root router including health check endpoint
5. **Dependency injection** — Set up FastAPI Depends() patterns for database session injection

## Capabilities

### New Capabilities

- **backend-app-configuration**: FastAPI app setup with CORS, middleware, and health check endpoint
- **database-connection**: SQLAlchemy session factory and database configuration
- **security-helpers**: Password hashing utilities and JWT helper structures

### Modified Capabilities

- (none) — This is foundational, no existing specs to modify

## Impact

- **Files created**: `app/main.py`, `app/core/config.py`, `app/core/database.py`, `app/core/security.py`, `app/api/__init__.py`
- **Dependencies added**: fastapi, uvicorn, sqlalchemy
- **Breaking changes**: None — this is new infrastructure