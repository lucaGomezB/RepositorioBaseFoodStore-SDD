# Tasks: setup-database-seed

## 1. Dependencies and Configuration

- [x] 1.1 Add alembic to backend/requirements.txt
- [x] 1.2 Install dependencies: `pip install -r requirements.txt`
- [x] 1.3 Run `alembic init alembic` in backend/ directory
- [x] 1.4 Configure alembic.ini with database URL from settings

## 2. Alembic Environment Setup

- [x] 2.1 Update backend/alembic/env.py to use SQLModel
- [x] 2.2 Import all models in env.py for auto-discovery
- [x] 2.3 Configure target_metadata from SQLModel declarative base
- [x] 2.4 Test: `alembic check` shows configuration is valid

## 3. Database Models

- [x] 3.1 Create backend/app/db/__init__.py module
- [x] 3.2 Create backend/app/db/base.py with SQLModel declarative base
- [x] 3.3 Create backend/app/models/rol.py (Rol table)
- [x] 3.4 Create backend/app/models/estado_pedido.py (EstadoPedido table)
- [x] 3.5 Create backend/app/models/forma_pago.py (FormaPago table)
- [x] 3.6 Create backend/app/models/usuario.py (Usuario table with FK to Rol)
- [x] 3.7 Create backend/app/models/__init__.py to export all models
- [x] 3.8 Test: Import all models without errors

## 4. Initial Migration

- [x] 4.1 Run: `alembic revision --autogenerate -m "initial create"`
- [x] 4.2 Review generated migration file
- [x] 4.3 Run: `alembic upgrade head`
- [x] 4.4 Verify: Tables are created in database
- [x] 4.5 Test: `alembic current` shows revision

## 5. Seed Data Module

- [x] 5.1 Create backend/app/db/seed.py
- [x] 5.2 Implement seed_roles() function with stable IDs
- [x] 5.3 Implement seed_estados_pedido() function with stable IDs
- [x] 5.4 Implement seed_formas_pago() function with stable IDs
- [x] 5.5 Implement seed_admin_user() function with hashed password
- [x] 5.6 Add idempotency check (skip if data exists)
- [x] 5.7 Create main() function that runs all seeds

## 6. Run Seed and Verify

- [x] 6.1 Run: `python -m app.db.seed`
- [x] 6.2 Verify: SELECT * FROM roles returns 4 rows
- [x] 6.3 Verify: SELECT * FROM estado_pedido returns 6 rows
- [x] 6.4 Verify: SELECT * FROM forma_pago returns 3 rows
- [x] 6.5 Verify: SELECT * FROM usuarios where email = 'admin@foodstore.com'
- [x] 6.6 Test: Run seed again — should complete without error

## 7. Git Commit

- [x] 7.1 Add files: `git add alembic/ alembic.ini app/db/ app/models/`
- [x] 7.2 Commit: `git commit -m "feat: setup database with migrations and seed data"`

## Summary

All tasks should result in:
- Alembic configured and working
- Database tables created (roles, estado_pedido, forma_pago, usuarios)
- Seed data populated with stable IDs
- Admin user created with hashed password
- Command `python -m app.db.seed` works