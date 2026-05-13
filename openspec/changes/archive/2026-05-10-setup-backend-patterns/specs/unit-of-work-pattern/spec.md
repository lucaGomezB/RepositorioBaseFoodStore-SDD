# Spec: unit-of-work-pattern

## Overview

This spec defines the Unit of Work pattern for managing database transactions across multiple repositories.

## ADDED Requirements

### Requirement: Unit of Work manages multiple repositories

The system SHALL provide a Unit of Work class that can hold multiple repositories and commit them as a single transaction.

#### Scenario: UoW holds multiple repositories
- **GIVEN** a Unit of Work instance
- **WHEN** adding multiple repositories (e.g., usuario_repo, pedido_repo)
- **THEN** both repositories share the same session

#### Scenario: UoW commits on exit
- **GIVEN** a Unit of Work with pending changes
- **WHEN** exiting the context manager (with block)
- **THEN** all changes are committed to the database

#### Scenario: UoW rolls back on exception
- **GIVEN** a Unit of Work with pending changes
- **WHEN** an exception occurs inside the with block
- **THEN** all changes are rolled back

### Requirement: UoW provides access to repositories

The system SHALL allow accessing registered repositories through attribute access.

#### Scenario: Access repository from UoW
- **GIVEN** a UoW with a usuario_repo registered
- **WHEN** accessing uow.usuario_repo
- **THEN** the repository instance is returned

### Requirement: UoW can register new repositories

The system SHALL allow registering repositories at runtime.

#### Scenario: Register a repository
- **GIVEN** a UoW instance and a repository class
- **WHEN** calling uow.register(UsuarioRepository)
- **THEN** a new repository instance is created and accessible via uow.usuario_repo