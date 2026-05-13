# Spec: base-repository-pattern

## Overview

This spec defines the generic BaseRepository[T] class that provides standard CRUD operations for all SQLModel entities.

## ADDED Requirements

### Requirement: BaseRepository[T] can be subclassed

The system SHALL provide a generic BaseRepository class that accepts any SQLModel as type parameter.

#### Scenario: Create a repository for a model
- **GIVEN** a SQLModel class (e.g., Usuario)
- **WHEN** creating `class UsuarioRepository(BaseRepository[Usuario])`
- **THEN** the repository is created without errors

#### Scenario: BaseRepository has create method
- **GIVEN** a BaseRepository subclass
- **WHEN** calling create() with a model instance
- **THEN** the instance is added to session and committed

#### Scenario: BaseRepository has get method
- **GIVEN** a BaseRepository subclass with data
- **WHEN** calling get(id) with a valid ID
- **THEN** the corresponding model instance is returned

#### Scenario: BaseRepository has get_all method
- **GIVEN** a BaseRepository subclass with data
- **WHEN** calling get_all()
- **THEN** a list of all instances is returned

#### Scenario: BaseRepository has update method
- **GIVEN** a BaseRepository subclass with data
- **WHEN** calling update(id, updates_dict)
- **THEN** the instance is updated and committed

#### Scenario: BaseRepository has delete method
- **GIVEN** a BaseRepository subclass with data
- **WHEN** calling delete(id)
- **THEN** the instance is deleted from database

### Requirement: Repository accepts session

The system SHALL allow passing a database session to the repository.

#### Scenario: Repository uses provided session
- **GIVEN** a database session
- **WHEN** creating a repository with that session
- **THEN** all operations use that session

### Requirement: Repository supports custom queries

The system SHALL allow adding custom query methods to subclasses.

#### Scenario: Custom query method can be added
- **GIVEN** a BaseRepository subclass
- **WHEN** adding a custom method that uses self.session
- **THEN** the custom query executes correctly