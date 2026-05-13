## ADDED Requirements

### Requirement: Display product catalog grid
The system SHALL display a responsive grid of product cards showing available products from the public catalog API.

#### Scenario: Show products in grid layout
- **WHEN** a user visits the homepage
- **THEN** the system SHALL display products in a responsive grid (1 col mobile, 4 cols desktop)
- **AND** each card SHALL show nombre, precio_base, imagen, hay_stock, and categorias

#### Scenario: Show skeleton while loading
- **WHEN** the catalog is loading
- **THEN** the system SHALL display skeleton cards with animated pulse effect

#### Scenario: Show empty state
- **WHEN** no products match the current filters
- **THEN** the system SHALL display a "No se encontraron productos" message

### Requirement: Search with debounce
The system SHALL provide a search input that filters products by name with a 300ms debounce.

#### Scenario: Search filters products
- **WHEN** a user types "pizza" in the search input
- **THEN** after 300ms, the system SHALL call the API with busqueda=pizza
- **AND** display only matching products

### Requirement: Filter by category
The system SHALL allow filtering products by category.

#### Scenario: Select category filter
- **WHEN** a user selects a category from the filter
- **THEN** the system SHALL call the API with the categoria_id parameter
- **AND** display only products in that category

### Requirement: Pagination
The system SHALL paginate the product catalog with page numbers and total count.

#### Scenario: Navigate pages
- **WHEN** a user clicks page 2
- **THEN** the system SHALL call the API with page=2
- **AND** display the next set of products

#### Scenario: Show total count
- **WHEN** the catalog loads
- **THEN** the system SHALL display "Mostrando X-Y de Z productos"

### Requirement: Product detail modal
The system SHALL show a detailed view of a product including ingredients (with allergen flag) and categories.

#### Scenario: Open product detail
- **WHEN** a user clicks a product card
- **THEN** the system SHALL display a modal with full product details
- **AND** the modal SHALL include: descripcion, precio, ingredientes (with ⚠️ for allergens), categorias, hay_stock

#### Scenario: Close product detail
- **WHEN** a user clicks the close button or outside the modal
- **THEN** the system SHALL close the modal
