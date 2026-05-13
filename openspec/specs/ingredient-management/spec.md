## ADDED Requirements

### Requirement: Create Ingredient
The system SHALL allow STOCK and ADMIN users to create ingredients with name, optional description, and required allergen flag.

#### Scenario: Create ingredient with allergen flag
- **WHEN** a STOCK user creates an ingredient with nombre and es_alergeno flag
- **THEN** the ingredient SHALL be created with the specified flag

#### Scenario: Cannot create duplicate ingredient name
- **WHEN** a user creates an ingredient with an existing name
- **THEN** the system SHALL return HTTP 400

### Requirement: List Ingredients (Public)
The system SHALL provide a public endpoint that returns all non-deleted ingredients, with optional filtering by allergen flag.

#### Scenario: Get all ingredients
- **WHEN** an unauthenticated user requests GET /ingredientes
- **THEN** the system SHALL return all active ingredients

#### Scenario: Filter by allergen
- **WHEN** a user requests GET /ingredientes?es_alergeno=true
- **THEN** the system SHALL return only ingredients marked as allergens

### Requirement: Update Ingredient
The system SHALL allow STOCK and ADMIN users to update ingredient name, description, and allergen flag.

#### Scenario: Update ingredient details
- **WHEN** a STOCK user updates an ingredient
- **THEN** the changes SHALL be persisted

### Requirement: Soft Delete Ingredient
The system SHALL allow STOCK and ADMIN users to soft-delete ingredients.

#### Scenario: Soft delete ingredient
- **WHEN** a STOCK user deletes an ingredient
- **THEN** the ingredient SHALL be marked as deleted
- **AND** SHALL NOT appear in GET /ingredientes
