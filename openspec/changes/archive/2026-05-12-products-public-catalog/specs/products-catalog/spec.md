## ADDED Requirements

### Requirement: Filter products by allergen exclusion
The system SHALL allow filtering the public product catalog to exclude products containing specific allergens (ingredients marked as es_alergeno).

#### Scenario: Exclude single allergen
- **WHEN** a user sends GET /api/v1/productos?excluir_alergenos=3
- **THEN** the system SHALL return only products that do NOT contain ingredient with id=3

#### Scenario: Exclude multiple allergens
- **WHEN** a user sends GET /api/v1/productos?excluir_alergenos=1,3,7
- **THEN** the system SHALL return products that do NOT contain ANY of the specified ingredients

#### Scenario: Allergen filter combined with other filters
- **WHEN** a user sends GET /api/v1/productos?excluir_alergenos=3&categoria_id=5
- **THEN** the system SHALL apply both filters

### Requirement: Paginated catalog with total count
The system SHALL support pagination via `page` and `limit` query parameters and include `total_count` in the response.

#### Scenario: Paginate with page and limit
- **WHEN** a user sends GET /api/v1/productos?page=2&limit=10
- **THEN** the system SHALL return products 11-20
- **AND** the response SHALL include `total_count` with the total number of matching products

#### Scenario: Default page and limit
- **WHEN** a user sends GET /api/v1/productos without page params
- **THEN** the system SHALL default to page=1, limit=20

### Requirement: Public catalog defaults to available products
The system SHALL filter the public catalog to show only available products (disponible=true) by default for unauthenticated users.

#### Scenario: Anonymous user sees only available products
- **WHEN** an unauthenticated user sends GET /api/v1/productos
- **THEN** the system SHALL return only products with disponible=true

#### Scenario: Authenticated user can override default
- **WHEN** an authenticated user sends GET /api/v1/productos?disponible=false
- **THEN** the system SHALL return products matching the filter regardless of default

## MODIFIED Requirements

### Requirement: Get single product
The system SHALL return full product details for available, non-deleted products. The response SHALL include ingredients (with allergen flag), categories, and a boolean `hay_stock` instead of the exact stock quantity.

#### Scenario: Get available product detail
- **WHEN** a user sends GET /api/v1/productos/{id} for an available, non-deleted product
- **THEN** the system SHALL return HTTP 200
- **AND** the response SHALL include: nombre, descripcion, precio_base, imagenes_url, hay_stock (boolean), categorias list, ingredientes list with es_alergeno flag

#### Scenario: Get unavailable product returns 404
- **WHEN** a user sends GET /api/v1/productos/{id} for a product with disponible=false
- **THEN** the system SHALL return HTTP 404 Not Found

#### Scenario: Get deleted product returns 404
- **WHEN** a user sends GET /api/v1/productos/{id} for a soft-deleted product
- **THEN** the system SHALL return HTTP 404 Not Found
