# Spec: seed-data

## Overview

This spec defines the initial data population for core entities required by the system.

## ADDED Requirements

### Requirement: Roles are seeded

The system SHALL populate the roles table with required roles.

#### Scenario: Roles table has 4 entries
- **GIVEN** the seed script has been run
- **WHEN** querying `SELECT * FROM roles;`
- **THEN** 4 rows are returned

#### Scenario: Role IDs are stable
- **GIVEN** the seed script runs
- **WHEN** checking role IDs
- **THEN** they match the design: ADMIN=1, STOCK=2, PEDIDOS=3, CLIENT=4

#### Scenario: Role names are correct
- **GIVEN** the seed script runs
- **WHEN** querying role names
- **THEN** they are: ADMIN, STOCK, PEDIDOS, CLIENT

---

### Requirement: EstadoPedido is seeded

The system SHALL populate the estado_pedido table with required states.

#### Scenario: EstadoPedido has 6 entries
- **GIVEN** the seed script has been run
- **WHEN** querying `SELECT * FROM estado_pedido;`
- **THEN** 6 rows are returned

#### Scenario: EstadoPedido IDs are stable
- **GIVEN** the seed script runs
- **WHEN** checking estado_pedido IDs
- **THEN** they match the design: PENDIENTE=1, CONFIRMADO=2, EN_PREPARACION=3, EN_CAMINO=4, ENTREGADO=5, CANCELADO=6

---

### Requirement: FormaPago is seeded

The system SHALL populate the forma_pago table with required payment methods.

#### Scenario: FormaPago has 3 entries
- **GIVEN** the seed script has been run
- **WHEN** querying `SELECT * FROM forma_pago;`
- **THEN** 3 rows are returned

#### Scenario: FormaPago IDs are stable
- **GIVEN** the seed script runs
- **WHEN** checking forma_pago IDs
- **THEN** they match the design: EFECTIVO=1, MERCADO_PAGO=2, TRANSFERENCIA=3

---

### Requirement: Admin user exists

The system SHALL create an admin user for initial access.

#### Scenario: Admin user is created
- **GIVEN** the seed script has been run
- **WHEN** querying for admin user
- **THEN** a user with email "admin@foodstore.com" exists

#### Scenario: Admin has ADMIN role
- **GIVEN** the admin user exists
- **WHEN** checking the user's role
- **THEN** the user has role_id=1 (ADMIN)

#### Scenario: Admin password is hashed
- **GIVEN** the admin user exists
- **WHEN** checking the password field
- **THEN** the password is a bcrypt hash, not plain text

---

### Requirement: Seed script is idempotent

The system SHALL allow running the seed script multiple times without errors.

#### Scenario: Second run succeeds
- **GIVEN** seed has been run once
- **WHEN** running `python -m app.db.seed` again
- **THEN** it completes without error (skips existing data)

---

### Requirement: Seed can be run as module

The system SHALL allow running the seed script as a Python module.

#### Scenario: Module execution works
- **GIVEN** the app is installed
- **WHEN** running `python -m app.db.seed`
- **THEN** the seed data is populated
- **AND** command exits with code 0