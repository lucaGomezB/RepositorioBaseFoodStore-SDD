## ADDED Requirements

### Requirement: Add to cart from catalog
The system SHALL provide an "Add to cart" button on each product card in the catalog.

#### Scenario: Add product from card
- **WHEN** a user clicks "Agregar" on a product card
- **THEN** the system SHALL add the product to the cart with quantity 1
- **AND** show a brief success indicator

### Requirement: Cart drawer
The system SHALL provide a slide-out drawer showing cart contents, accessible from any page.

#### Scenario: Open cart drawer
- **WHEN** a user clicks the cart badge in the header
- **THEN** the system SHALL slide in a drawer from the right
- **AND** show cart items with quantities and total

#### Scenario: Close cart drawer
- **WHEN** a user clicks outside the drawer or the close button
- **THEN** the system SHALL close the drawer

### Requirement: Cart badge
The system SHALL show the item count in the header as a badge.

#### Scenario: Badge updates on add/remove
- **WHEN** items are added or removed from cart
- **THEN** the badge count SHALL update in real-time

### Requirement: Floating cart indicator
The system SHALL show a floating cart button with item count on all pages.

#### Scenario: Floating cart visible
- **WHEN** a user scrolls any page
- **THEN** a floating cart button SHALL be visible in the bottom-right corner
- **AND** show the current item count
