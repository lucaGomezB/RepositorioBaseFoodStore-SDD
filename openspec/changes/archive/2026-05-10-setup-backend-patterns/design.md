# Design: setup-backend-patterns

## Context

The database is set up with migrations and seed data (setup-database-seed), but each module would need to implement its own data access logic. Without consistent patterns, code becomes inconsistent, harder to test, and difficult to maintain.

This change establishes infrastructure patterns that all feature modules will follow.

## Goals / Non-Goals

**Goals:**
- Create BaseRepository[T] with generic CRUD methods
- Implement Unit of Work for transactional operations
- Set up FastAPI Depends() patterns for dependency injection
- Ensure all patterns are testable with pytest

**Non-Goals:**
- Implementing specific feature repositories — each feature will implement its own
- Adding business logic — that's in the service layer per feature
- Setting up caching — future change

## Decisions

### 1. Generic BaseRepository[T] over specific repositories
**Decision**: Use a generic BaseRepository[T] that any SQLModel can extend.
**Rationale**: Reduces boilerplate, ensures consistent API across all repositories.
**Alternative considered**: Individual repository per model — rejected, too much repetition.

### 2. Unit of Work with context manager
**Decision**: Implement UoW as a context manager that commits on exit.
**Rationale**: Pythonic, ensures cleanup, easy to use in FastAPI endpoints.
**Alternative considered**: Manual begin/commit — rejected, error-prone.

### 3. FastAPI Depends() for session injection
**Decision**: Use get_db() from setup-backend-config as the session source.
**Rationale**: Already configured, consistent with existing setup.
**Alternative considered**: Create new dependency — rejected, would duplicate.

### 4. RepositoryFactory for complex queries
**Decision**: Create a factory function that returns repositories with session.
**Rationale**: Supports complex queries that need custom methods beyond CRUD.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-------------|
| Session management issues | Data not saved or partial saves | UoW ensures commit on exit |
| Circular imports | Import errors between modules | Keep patterns in app.core, not app.modules |
| Performance overhead | Extra abstraction layer | Use lazy loading, only import what's needed |

## Open Questions

- Should BaseRepository support pagination?
  - **Current decision**: Add paginate() method, not in base generic
- Should we use async SQLAlchemy?
  - **Current decision**: Keep sync for now, migrate later if needed