# Spec: database-connection

## Overview

This spec defines the SQLAlchemy database configuration, session factory, and dependency injection pattern for database sessions.

## ADDED Requirements

### Requirement: Database connection configuration exists

The system SHALL configure database connection using environment variables.

#### Scenario: Database URL is loaded from environment
- **GIVEN** DATABASE_URL is set in environment
- **WHEN** importing `from app.core.database import engine`
- **THEN** the engine is created with the configured DATABASE_URL

#### Scenario: App fails gracefully when no DATABASE_URL
- **GIVEN** DATABASE_URL is not set
- **WHEN** importing `from app.core.database import engine`
- **THEN** an appropriate error is raised with helpful message

---

### Requirement: Session factory is available

The system SHALL provide a SQLAlchemy session factory.

#### Scenario: Session can be created
- **GIVEN** the database is configured
- **WHEN** creating a session with `Session()`
- **THEN** a valid session object is returned

#### Scenario: Session can be closed
- **GIVEN** a session is open
- **WHEN** calling `session.close()`
- **THEN** the session resources are released

---

### Requirement: Dependency injection pattern implemented

The system SHALL provide a FastAPI dependency for database sessions.

#### Scenario: get_db dependency works
- **GIVEN** a FastAPI route with `Depends(get_db)`
- **WHEN** a request is made to that route
- **THEN** a database session is injected into the endpoint function
- **AND** the session is automatically closed after the request

#### Scenario: Multiple requests get separate sessions
- **GIVEN** the get_db dependency is used
- **WHEN** two concurrent requests hit the same endpoint
- **THEN** each request gets its own separate session instance

---

### Requirement: Database configuration is modular

The system SHALL separate database configuration from application code.

#### Scenario: Database module exists independently
- **GIVEN** the app/core/ directory exists
- **WHEN** checking for database.py
- **THEN** the file exists and can be imported without loading the entire app

#### Scenario: Engine is reusable across the application
- **GIVEN** the database module is imported multiple times
- **WHEN** accessing the engine
- **THEN** the same engine instance is returned (singleton pattern)