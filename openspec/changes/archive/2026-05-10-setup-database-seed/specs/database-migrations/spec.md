# Spec: database-migrations

## Overview

This spec defines the Alembic migration system for version-controlled database schema changes.

## ADDED Requirements

### Requirement: Alembic initialized in backend

The system SHALL have Alembic properly configured in the backend directory.

#### Scenario: Alembic directory exists
- **GIVEN** the backend directory
- **WHEN** checking for alembic/ directory
- **THEN** the directory exists with env.py and script.py.mako

#### Scenario: Alembic.ini exists
- **GIVEN** the backend directory
- **WHEN** checking for alembic.ini
- **THEN** the file exists and is valid configuration

---

### Requirement: Alembic can connect to database

The system SHALL configure Alembic to use the same DATABASE_URL as the application.

#### Scenario: env.py uses app config
- **GIVEN** alembic/env.py exists
- **WHEN** importing and checking the database URL
- **THEN** it uses the same DATABASE_URL from settings

---

### Requirement: Initial migration can be created

The system SHALL allow creating an initial migration.

#### Scenario: Revision command works
- **GIVEN** Alembic is configured
- **WHEN** running `alembic revision --autogenerate -m "initial"`
- **THEN** a migration file is created in alembic/versions/

#### Scenario: Migration can upgrade
- **GIVEN** a migration file exists
- **WHEN** running `alembic upgrade head`
- **THEN** the migration applies without errors

#### Scenario: Migration can downgrade
- **GIVEN** a migration has been applied
- **WHEN** running `alembic downgrade -1`
- **THEN** the migration is reverted without errors

---

### Requirement: Migration tracks current version

The system SHALL track which migration is the current HEAD.

#### Scenario: Current revision is recorded
- **GIVEN** migrations have been applied
- **WHEN** running `alembic current`
- **THEN** it shows the current revision identifier

#### Scenario: History shows all migrations
- **GIVEN** multiple migrations exist
- **WHEN** running `alembic history`
- **THEN** it shows all migrations in order