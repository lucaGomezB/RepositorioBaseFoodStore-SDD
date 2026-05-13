## Why

El catálogo de productos es el núcleo del sistema Food Store. Sin un CRUD completo de productos no es posible operar el catálogo público, el carrito de compras, los pedidos, ni los pagos. Actualmente existe una implementación parcial del backend que carece de gestión de stock, soft delete, y roles correctos. El frontend de gestión no existe. Este cambio completa el CRUD faltante para que los roles ADMIN y STOCK puedan administrar productos.

## What Changes

- **Backend — Modelo `Producto`**: Agregar campos `stock_cantidad` (entero >= 0) y `eliminado_en` (soft delete timestamp) con su migración Alembic.
- **Backend — Soft delete real**: Reemplazar el delete dummy por soft delete con filtro automático en queries.
- **Backend — Roles**: Corregir la protección de endpoints de productos para aceptar `[ADMIN, STOCK]` en lugar de solo `ADMIN`.
- **Backend — Endpoint stock**: Agregar `PATCH /api/v1/productos/{id}/stock` con actualización atómica (US-021).
- **Backend — Filtros GET**: Agregar filtros por categoría, búsqueda por nombre, y disponibilidad al listado de productos.
- **Frontend — Entities**: Crear `entities/product/` con tipos, schemas, y hooks base.
- **Frontend — CRUD pages**: Crear páginas de gestión de productos (listado, formulario create/edit, stock updater, soft delete).
- **Frontend — Features**: Componentes reutilizables del catálogo para usar en gestión y público.

## Capabilities

### New Capabilities
- `products-catalog`: CRUD de productos del catálogo con stock, soft delete, roles, y frontend de gestión.

### Modified Capabilities
- *(ninguna — es la primera spec de productos)*

## Impact

- **Backend**: `backend/app/models/producto.py`, `backend/app/core/schemas/producto.py`, `backend/app/core/services/producto.py`, `backend/app/core/repositories/producto.py`, `backend/app/api/productos.py`, `backend/app/alembic/versions/` (nueva migración)
- **Frontend**: `frontend/src/entities/product/` (nuevo), `frontend/src/features/catalog/` (nuevo), `frontend/src/pages/` (nuevas páginas de gestión)
- **Dependencias**: Utiliza `require_roles(["ADMIN", "STOCK"])` del módulo auth-rbac-roles existente
