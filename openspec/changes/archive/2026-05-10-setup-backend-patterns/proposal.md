# Proposal: setup-backend-patterns

## Why

The database and migrations are in place (setup-database-seed), but there's no consistent pattern for data access. We need BaseRepository[T], Unit of Work, and FastAPI dependency injection patterns to ensure consistent, maintainable, and testable code across all feature modules.

## What Changes

1. **BaseRepository[T]** — Generic repository class with CRUD operations (create, get, get_all, update, delete)
2. **Unit of Work** — Context manager pattern for transactional operations across multiple repositories
3. **FastAPI Depends() patterns** — Standardized dependency injection for database sessions and repositories
4. **Base service layer** — Abstract service class with common operations
5. **RepositoryFactory** — Factory for creating repositories with session injection

## Capabilities

### New Capabilities

- **base-repository-pattern**: Generic BaseRepository[T] class with standard CRUD operations
- **unit-of-work-pattern**: Unit of Work implementation for transaction management
- **dependency-injection-pattern**: FastAPI Depends() patterns for repositories and services

### Modified Capabilities

- (none) — This is infrastructure patterns, no existing specs to modify

## Impact

- **Files created**: `app/core/repositories/base.py`, `app/core/uow.py`, `app/core/dependencies.py`
- **Breaking changes**: None — this adds patterns, doesn't change existing code
- **Depends on**: setup-database-seed