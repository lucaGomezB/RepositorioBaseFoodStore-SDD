# Proposal: setup-database-seed

## Why

The backend config is in place (setup-backend-config), but there's no database setup. We need PostgreSQL configured with Alembic for migrations and seed data (Roles, EstadoPedido, FormaPago, admin user) before any feature that requires data storage can be developed.

## What Changes

1. **Alembic configuration** — Set up Alembic for database migrations with proper directory structure
2. **Initial migration** — Create the first migration that sets up the base tables
3. **Seed data module** — Create `app/db/seed.py` to populate initial data:
   - Roles: ADMIN, STOCK, PEDIDOS, CLIENT
   - EstadoPedido: PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO
   - FormaPago: EFECTIVO, MERCADO_PAGO, TRANSFERENCIA
   - Usuario admin: email admin@foodstore.com, password hasheada
4. **Database connection test** — Verify connection to PostgreSQL works

## Capabilities

### New Capabilities

- **database-migrations**: Alembic setup for version-controlled schema migrations
- **seed-data**: Initial data population for core entities (Roles, EstadoPedido, FormaPago, admin user)

### Modified Capabilities

- (none) — This is foundational, no existing specs to modify

## Impact

- **Files created**: `alembic.ini`, `alembic/` directory, `app/db/seed.py`
- **Dependencies added**: alembic
- **Breaking changes**: None — this is new infrastructure
- **Requires**: PostgreSQL running and accessible via DATABASE_URL