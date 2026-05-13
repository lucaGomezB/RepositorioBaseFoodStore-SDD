## Why

El sistema necesita gestionar categorías de productos con jerarquía (padre-hijo) para organizar el catálogo. Actualmente existe el modelo `Categoria` y el repositorio, pero no hay endpoints CRUD, ni service layer, ni validación de reglas de negocio (sin ciclos, sin auto-referencia, soft delete).

## What Changes

- Crear schemas Pydantic para request/response de categorías
- Crear service layer con validaciones: nombre único, sin ciclos en jerarquía, soft delete
- Crear router CRUD: GET /categorias (público árbol), POST/PUT/DELETE /categorias (solo STOCK y ADMIN)
- Agregar tests de integración

## Capabilities

### New Capabilities
- `category-management`: CRUD completo de categorías jerárquicas con CTE recursivo

### Modified Capabilities
- (ninguna)

## Impact

- **Backend**: Nuevos archivos `app/schemas/categoria.py`, `app/services/categoria.py`, `app/api/categorias.py`
- **API**: Endpoints: GET /api/v1/categorias (público), POST/PUT/DELETE (STOCK/ADMIN)
- **Dependencias**: `auth-rbac-roles` para proteger endpoints
