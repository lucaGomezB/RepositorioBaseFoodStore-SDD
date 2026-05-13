# Design: setup-database-seed

## Context

The backend config is complete (setup-backend-config) with:
- SQLAlchemy engine configured via DATABASE_URL
- pydantic-settings for config management
- FastAPI app with CORS middleware

This change adds Alembic for migrations and seed data for core entities.

## Goals / Non-Goals

**Goals:**
- Set up Alembic with proper configuration in backend/
- Create initial migration with basic tables
- Populate seed data: Roles, EstadoPedido, FormaPago, admin user
- Verify database connection works

**Non-Goals:**
- Full schema definition (tables for users, products, orders) — handled in feature changes
- Data validation beyond basic integrity constraints
- Production deployment scripts

## Decisions

### 1. Alembic location
**Decision**: Place Alembic configuration in backend/ root (alongside requirements.txt).
**Rationale**: Standard location, matches SQLAlchemy convention.
**Alternative considered**: Inside app/ — rejected, better to keep infrastructure at root.

### 2. Migration approach
**Decision**: Use SQLModel as the source of truth (model_class parameter in env.py).
**Rationale**: Single source of truth for schema, automatic migration generation.
**Alternative considered**: Manual migrations — rejected, error-prone.

### 3. Seed data IDs
**Decision**: Use explicit IDs for seed data (not auto-increment).
**Rationale**: RN-DA02 requirement — IDs must be stable for foreign key references.
**Alternative considered**: Auto-increment — rejected, violates stability requirement.

### 4. Seed data module location
**Decision**: Create `app/db/seed.py` module (not a script).
**Rationale**: Can be imported, easier to test, follows Python module conventions.
**Alternative considered**: CLI script — rejected, less flexible.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-------------|
| PostgreSQL not running | App fails | Clear error message, documentation |
| DATABASE_URL invalid | Connection fails | Validate before running migrations |
| Seed already run | Duplicate data | Check if data exists before inserting |
| Wrong ID references | FK constraint fails | Explicit IDs match design spec |

## Migration Plan

1. Add `alembic` to requirements.txt
2. Run `alembic init alembic` to create directory structure
3. Configure `alembic.ini` and `alembic/env.py` to use SQLModel
4. Create initial migration: `alembic revision --autogenerate -m "initial"`
5. Run `alembic upgrade head` to apply
6. Run seed: `python -m app.db.seed`
7. Verify: `SELECT * FROM roles;` returns 4 rows

## Open Questions

- Should we include a "reset" or "reseed" capability?
  - **Current decision**: Not in this change — add later if needed
- Should the admin password be configurable via env?
  - **Current decision**: Yes, use ADMIN_PASSWORD from env (default: "admin123")