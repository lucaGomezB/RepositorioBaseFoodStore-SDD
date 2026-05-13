# products-catalog Specification

## Purpose
CRUD de productos del catálogo con gestión de stock, soft delete, roles de acceso (ADMIN/STOCK), filtros de búsqueda, frontend de gestión, y endpoints públicos de catálogo con detalle expandido.

## Requirements

### Requirement: Create product
The system SHALL allow users with role ADMIN or STOCK to create a new product with nombre, descripción, precio (NUMERIC(10,2)), stock_cantidad (Integer >= 0), imagen URL, and disponibilidad (Boolean, default true).

#### Scenario: Admin creates product successfully
- **WHEN** an authenticated user with role ADMIN sends POST /api/v1/productos with valid fields
- **THEN** the system SHALL return HTTP 201 with the created product data
- **AND** the response SHALL include id, nombre, descripcion, precio_base, stock_cantidad, disponible, fecha_creacion

#### Scenario: Stock manager creates product successfully
- **WHEN** an authenticated user with role STOCK sends POST /api/v1/productos with valid fields
- **THEN** the system SHALL return HTTP 201 with the created product data

#### Scenario: Create product with negative stock
- **WHEN** an authenticated user sends POST /api/v1/productos with stock_cantidad = -1
- **THEN** the system SHALL return HTTP 422 with validation error

#### Scenario: Client cannot create product
- **WHEN** an authenticated user with role CLIENT sends POST /api/v1/productos
- **THEN** the system SHALL return HTTP 403 Forbidden

### Requirement: Update product
The system SHALL allow users with role ADMIN or STOCK to update any field of an existing product except id and fecha_creacion.

#### Scenario: Update product fields
- **WHEN** an authenticated user with role STOCK sends PATCH /api/v1/productos/{id} with valid updated fields
- **THEN** the system SHALL return HTTP 200 with the updated product data
- **AND** fecha_actualizacion SHALL be updated

#### Scenario: Update nonexistent product
- **WHEN** an authenticated user sends PATCH /api/v1/productos/99999
- **THEN** the system SHALL return HTTP 404 Not Found

#### Scenario: Update price with invalid precision
- **WHEN** an authenticated user sends PATCH /api/v1/productos/{id} with precio_base having more than 2 decimal places
- **THEN** the system SHALL return HTTP 422 with validation error

### Requirement: Update stock
The system SHALL allow users with role ADMIN or STOCK to update the stock quantity of a product atomically.

#### Scenario: Increment stock
- **WHEN** an authenticated user sends PATCH /api/v1/productos/{id}/stock with {"cantidad": 10}
- **THEN** the system SHALL increment stock_cantidad by 10
- **AND** return HTTP 200 with the new stock_cantidad

#### Scenario: Decrement stock to zero
- **WHEN** an authenticated user sends PATCH /api/v1/productos/{id}/stock with {"cantidad": -5} where current stock is 10
- **THEN** the system SHALL decrement stock_cantidad to 5
- **AND** return HTTP 200

#### Scenario: Decrement below zero is rejected
- **WHEN** an authenticated user sends PATCH /api/v1/productos/{id}/stock with {"cantidad": -100} where current stock is 5
- **THEN** the system SHALL return HTTP 400 with detail "Insufficient stock"
- **AND** stock_cantidad SHALL remain unchanged

#### Scenario: Update stock on nonexistent product
- **WHEN** an authenticated user sends PATCH /api/v1/productos/99999/stock
- **THEN** the system SHALL return HTTP 404 Not Found

### Requirement: Soft delete product
The system SHALL allow users with role ADMIN or STOCK to soft delete a product by setting eliminado_en timestamp.

#### Scenario: Soft delete product
- **WHEN** an authenticated user with role ADMIN sends DELETE /api/v1/productos/{id}
- **THEN** the system SHALL set eliminado_en to current timestamp
- **AND** return HTTP 204 No Content

#### Scenario: Deleted product excluded from list
- **WHEN** a user calls GET /api/v1/productos after soft delete
- **THEN** the deleted product SHALL NOT appear in the response

#### Scenario: Soft delete nonexistent product
- **WHEN** an authenticated user sends DELETE /api/v1/productos/99999
- **THEN** the system SHALL return HTTP 404 Not Found

### Requirement: List products with filters (admin)
The system SHALL allow listing products with optional filters: categoria_id, busqueda (nombre LIKE), disponible, and incluir_eliminados (admin only).

#### Scenario: List all available products
- **WHEN** a user sends GET /api/v1/productos
- **THEN** the system SHALL return HTTP 200 with a list of non-deleted products

#### Scenario: Filter by category
- **WHEN** a user sends GET /api/v1/productos?categoria_id=5
- **THEN** the system SHALL return only products associated with category id=5

#### Scenario: Search by name
- **WHEN** a user sends GET /api/v1/productos?busqueda=pizza
- **THEN** the system SHALL return products whose nombre contains "pizza" (case-insensitive)

#### Scenario: Filter by availability
- **WHEN** a user sends GET /api/v1/productos?disponible=false
- **THEN** the system SHALL return only products where disponible is false

### Requirement: Public catalog listing
The system SHALL provide a public catalog endpoint that lists available, non-deleted products with pagination, search, category filter, and allergen exclusion.

#### Scenario: Anonymous user sees only available products
- **WHEN** an unauthenticated user sends GET /api/v1/catalogo/productos
- **THEN** the system SHALL return only products with disponible=true and eliminado_en IS NULL
- **AND** the response SHALL include `total_count` with the total number of matching products

#### Scenario: Paginate with page and limit
- **WHEN** a user sends GET /api/v1/catalogo/productos?page=2&limit=10
- **THEN** the system SHALL return products 11-20
- **AND** the response SHALL include `total_count`

#### Scenario: Filter by category in public catalog
- **WHEN** a user sends GET /api/v1/catalogo/productos?categoria_id=5
- **THEN** the system SHALL return only products in category id=5

#### Scenario: Search by name in public catalog
- **WHEN** a user sends GET /api/v1/catalogo/productos?busqueda=pizza
- **THEN** the system SHALL return products whose nombre contains "pizza" (case-insensitive)

#### Scenario: Exclude allergens from catalog
- **WHEN** a user sends GET /api/v1/catalogo/productos?excluir_alergenos=1,3,7
- **THEN** the system SHALL return only products that do NOT contain ANY of ingredients 1, 3, or 7

### Requirement: Get single product (admin)
The system SHALL return full product details by ID, including all fields.

#### Scenario: Get existing product
- **WHEN** a user sends GET /api/v1/productos/{id}
- **THEN** the system SHALL return HTTP 200 with all product fields

#### Scenario: Get nonexistent product
- **WHEN** a user sends GET /api/v1/productos/99999
- **THEN** the system SHALL return HTTP 404 Not Found

### Requirement: Get single product (public catalog)
The system SHALL return full product details for available, non-deleted products. The response SHALL include ingredients (with allergen flag), categories, and a boolean `hay_stock` instead of the exact stock quantity.

#### Scenario: Get available product detail
- **WHEN** a user sends GET /api/v1/catalogo/productos/{id} for an available, non-deleted product
- **THEN** the system SHALL return HTTP 200
- **AND** the response SHALL include: nombre, descripcion, precio_base, imagenes_url, hay_stock (boolean), categorias list, ingredientes list with es_alergeno flag

#### Scenario: Get unavailable product returns 404
- **WHEN** a user sends GET /api/v1/catalogo/productos/{id} for a product with disponible=false
- **THEN** the system SHALL return HTTP 404 Not Found

#### Scenario: Soft-deleted product returns 404 in public catalog
- **WHEN** a user sends GET /api/v1/catalogo/productos/{id} for a soft-deleted product
- **THEN** the system SHALL return HTTP 404 Not Found
