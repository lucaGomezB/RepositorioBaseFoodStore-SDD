# Spec: cart-store

## Overview

Smart cart store with stock validation, price calculation, and localStorage persistence.

## ADDED Requirements

### Requirement: Can add items to cart

The system SHALL allow adding products to the cart.

#### Scenario: Add item with sufficient stock
- **WHEN** adding product with quantity 2 and stock >= 2
- **THEN** item is added to cart
- **AND** itemCount and totalAmount are updated correctly

#### Scenario: Add item with insufficient stock
- **WHEN** adding product with quantity 5 but stock is 3
- **THEN** addItem returns false (not added)
- **AND** cart remains unchanged

#### Scenario: Add existing item (increment)
- **WHEN** adding same product that already exists in cart
- **AND** current qty + new qty <= stock
- **THEN** quantity is incremented (not duplicated)

### Requirement: Can remove items from cart

The system SHALL allow removing products from the cart.

#### Scenario: Remove item by productId
- **WHEN** removeItem(productId) is called
- **THEN** item is removed from cart
- **AND** totals are recalculated

### Requirement: Can update item quantity

The system SHALL allow changing quantity of items in cart.

#### Scenario: Update quantity within stock limit
- **WHEN** updateQuantity(productId, 3) with stock >= 3
- **THEN** quantity is updated to 3

#### Scenario: Update quantity exceeds stock
- **WHEN** updateQuantity(productId, 10) but stock is 5
- **THEN** returns false, quantity unchanged

### Requirement: Cart persists across page reloads

The system SHALL persist cart to localStorage using Zustand persist middleware.

#### Scenario: Reload page preserves cart
- **WHEN** user adds items to cart and refreshes the page
- **AND** localStorage is not cleared
- **THEN** cart items are restored with same quantities

### Requirement: Cart calculates totals automatically

The system SHALL maintain running totals for item count and amount.

#### Scenario: Add item updates totals
- **WHEN** item added to empty cart
- **THEN** itemCount = 1, totalAmount = product.precio_base * quantity

#### Scenario: Multiple items with customizations
- **WHEN** items with customizations added
- **THEN** each item's price includes base + customization cost (if any)