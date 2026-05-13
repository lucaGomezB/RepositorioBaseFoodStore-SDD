## ADDED Requirements

### Requirement: Create Category
The system SHALL allow STOCK and ADMIN users to create categories with a name, optional description, optional parent_id, and display order.

#### Scenario: Create root category
- **WHEN** a STOCK user creates a category without parent_id
- **THEN** the category SHALL be created as a root category
- **AND** the system SHALL return the created category

#### Scenario: Create subcategory
- **WHEN** a STOCK user creates a category with a valid parent_id
- **THEN** the category SHALL be created as a child of the specified parent

#### Scenario: Cannot create category with non-existent parent
- **WHEN** a user creates a category with an invalid parent_id
- **THEN** the system SHALL return HTTP 400

### Requirement: List Categories (Public Tree)
The system SHALL provide a public endpoint that returns all non-deleted categories as a hierarchical tree.

#### Scenario: Get category tree
- **WHEN** an unauthenticated user requests GET /categorias
- **THEN** the system SHALL return a tree of all active categories

#### Scenario: Tree includes nested children
- **WHEN** categories have parent-child relationships
- **THEN** each category node SHALL include a `subcategorias` array with its children

### Requirement: Update Category
The system SHALL allow STOCK and ADMIN users to update category name, description, parent_id, and display order.

#### Scenario: Update category name
- **WHEN** a STOCK user updates a category's name
- **THEN** the change SHALL be persisted

#### Scenario: Cannot create cycle in hierarchy
- **WHEN** a user sets a category's parent to one of its own descendants
- **THEN** the system SHALL return HTTP 400 with detail "Cannot create circular reference"

### Requirement: Soft Delete Category
The system SHALL allow STOCK and ADMIN users to soft-delete categories by setting deleted_at.

#### Scenario: Soft delete category
- **WHEN** a STOCK user deletes a category
- **THEN** the category SHALL be marked with a deleted_at timestamp
- **AND** SHALL NOT appear in the public tree
