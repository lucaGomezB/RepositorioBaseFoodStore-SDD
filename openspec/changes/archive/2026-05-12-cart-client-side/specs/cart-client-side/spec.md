## ADDED Requirements

### Requirement: Add product to cart
The system SHALL allow adding products to the cart with quantity and optional ingredient exclusions.

#### Scenario: Add product
- **WHEN** a user clicks "Add to cart" on a product
- **THEN** the system SHALL add the product to the Zustand cart store
- **AND** persist to localStorage

#### Scenario: Add same product again increments quantity
- **WHEN** a user adds a product already in the cart
- **THEN** the system SHALL increment the quantity instead of duplicating

### Requirement: Customize product (exclude ingredients)
The system SHALL allow excluding specific ingredients from a cart item.

#### Scenario: Exclude ingredient
- **WHEN** a user selects ingredients to exclude from a product
- **THEN** the system SHALL store the exclusiones as ingredient IDs

### Requirement: Modify quantity
The system SHALL allow changing the quantity of a cart item. Setting to 0 removes it.

#### Scenario: Update quantity
- **WHEN** a user changes quantity of an item
- **THEN** the system SHALL update the stored quantity

#### Scenario: Quantity 0 removes item
- **WHEN** a user sets quantity to 0
- **THEN** the system SHALL remove the item from cart

### Requirement: Remove item from cart
The system SHALL allow removing a single item from the cart.

#### Scenario: Remove item
- **WHEN** a user clicks remove on a cart item
- **THEN** the system SHALL remove it from the store

### Requirement: View cart summary
The system SHALL display cart items with quantities, prices, subtotal, and total.

#### Scenario: Empty cart
- **WHEN** the cart is empty
- **THEN** the system SHALL show a message and link to the catalog

#### Scenario: Cart with items
- **WHEN** the cart has items
- **THEN** the system SHALL show each item with name, quantity, price, and total

### Requirement: Clear cart
The system SHALL allow clearing all items from the cart with confirmation.

#### Scenario: Clear cart with confirmation
- **WHEN** a user clicks "Clear cart"
- **THEN** the system SHALL show a confirmation dialog before clearing
