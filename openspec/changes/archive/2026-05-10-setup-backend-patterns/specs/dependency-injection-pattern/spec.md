# Spec: dependency-injection-pattern

## Overview

This spec defines the FastAPI dependency injection patterns for database sessions and repositories.

## ADDED Requirements

### Requirement: get_db provides session dependency

The system SHALL provide a FastAPI dependency that yields a database session.

#### Scenario: get_db yields session
- **WHEN** using get_db() as a FastAPI dependency
- **THEN** a database session is yielded to the endpoint

#### Session is closed after request
- **GIVEN** a get_db dependency in use
- **WHEN** the request completes
- **THEN** the session is properly closed

### Requirement: Repository dependency factories

The system SHALL provide a way to create repository dependencies that automatically use the session from get_db.

#### Scenario: Repository Depends() works in endpoint
- **GIVEN** a repository factory configured
- **WHEN** using Depends(get_usuario_repo) in a route
- **THEN** a repository with the current session is injected

#### Scenario: Multiple repositories share session
- **GIVEN** a route with multiple repository dependencies
- **WHEN** the route executes
- **THEN** all repositories use the same session

### Requirement: UoW dependency for transactions

The system SHALL provide a UoW dependency for endpoints that need transaction management.

#### Scenario: UoW Depends() works in endpoint
- **WHEN** using Depends(get_uow) in a route
- **THEN** a Unit of Work instance is injected

#### UoW commits on successful response
- **GIVEN** a get_uow dependency in use
- **WHEN** the endpoint returns successfully
- **THEN** all pending changes are committed

#### UoW rolls back on error
- **GIVEN** a get_uow dependency in use
- **WHEN** the endpoint raises an exception
- **THEN** all pending changes are rolled back