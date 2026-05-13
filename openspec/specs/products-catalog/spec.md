## ADDED Requirements

### Requirement: Replace product ingredients (bulk)
The system SHALL allow users with role ADMIN or STOCK to replace ALL ingredients of a product atomically via PUT, receiving an array of ingredient assignments.

#### Scenario: Replace all ingredients for a product
- **WHEN** an authenticated user with role STOCK sends PUT /api/v1/productos/{id}/ingredientes with a valid array of ingredient assignments
- **THEN** the system SHALL remove all existing ingredient relationships for that product
- **AND** the system SHALL create the new ingredient relationships
- **AND** return HTTP 200 with the updated ingredient list

#### Scenario: Replace ingredients on nonexistent product
- **WHEN** an authenticated user sends PUT /api/v1/productos/99999/ingredientes
- **THEN** the system SHALL return HTTP 404 Not Found

#### Scenario: Replace with empty array removes all ingredients
- **WHEN** an authenticated user sends PUT /api/v1/productos/{id}/ingredientes with []
- **THEN** the system SHALL remove all ingredient relationships
- **AND** return HTTP 200 with an empty list

### Requirement: Replace product categories (bulk)
The system SHALL allow users with role ADMIN or STOCK to replace ALL categories of a product atomically via PUT, receiving an array of category assignments.

#### Scenario: Replace all categories for a product
- **WHEN** an authenticated user with role STOCK sends PUT /api/v1/productos/{id}/categorias with a valid array of category assignments
- **THEN** the system SHALL remove all existing category relationships for that product
- **AND** the system SHALL create the new category relationships
- **AND** return HTTP 200 with the updated category list

#### Scenario: Replace categories on nonexistent product
- **WHEN** an authenticated user sends PUT /api/v1/productos/99999/categorias
- **THEN** the system SHALL return HTTP 404 Not Found

#### Scenario: Replace with empty array removes all categories
- **WHEN** an authenticated user sends PUT /api/v1/productos/{id}/categorias with []
- **THEN** the system SHALL remove all category relationships
- **AND** return HTTP 200 with an empty list

### Requirement: No duplicate relationships
The system SHALL enforce unique (producto_id, categoria_id) and (producto_id, ingrediente_id) constraints to prevent duplicate relationships.

#### Scenario: Adding duplicate category returns error
- **WHEN** an authenticated user tries to add the same category twice to a product
- **THEN** the system SHALL return HTTP 409 Conflict

#### Scenario: Adding duplicate ingredient returns error
- **WHEN** an authenticated user tries to add the same ingredient twice to a product
- **THEN** the system SHALL return HTTP 409 Conflict
