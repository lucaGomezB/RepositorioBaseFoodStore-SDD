## Why

El CRUD de productos (products-catalog-crud) ya permite crear, editar, gestionar stock y eliminar productos. Pero los productos no tienen sentido sin sus relaciones: un producto debe pertenecer a categorías y estar compuesto por ingredientes. Las US-016 y US-017 lo exigen. Además, existe un bug runtime en los métodos `add_ingrediente` y `add_categoria` que hace que los endpoints POST de relaciones fallen con AttributeError.

## What Changes

- **Backend — Endpoint PUT ingredientes**: Agregar `PUT /api/v1/productos/{id}/ingredientes` que reemplaza TODOS los ingredientes de un producto atómicamente (delete all + insert all en una transacción).
- **Backend — Endpoint PUT categorías**: Agregar `PUT /api/v1/productos/{id}/categorias` que reemplaza TODAS las categorías de un producto atómicamente.
- **Backend — Bugfix**: Corregir `add_ingrediente()` y `add_categoria()` en el service para acceder dict con `data["key"]` en vez de `data.key`.
- **Backend — Constraints UNIQUE**: Agregar unique constraints compuestas en `producto_categoria(producto_id, categoria_id)` y `producto_ingrediente(producto_id, ingrediente_id)` para evitar duplicados + migración.
- **Backend — Tests**: Tests completos para todos los endpoints de relaciones (GET, POST, PUT, DELETE).
- **Frontend**: No aplica (las relaciones se gestionan desde el backend por ahora; el frontend de gestión de productos se actualiza en un change posterior).

## Capabilities

### Modified Capabilities
- `products-catalog`: Se agregan requirements para PUT de reemplazo completo de relaciones M2M (ingredientes y categorías).

## Impact

- **Backend**: `backend/app/core/services/producto.py` (bugfix + PUT endpoints), `backend/app/api/productos.py` (nuevos endpoints PUT), `backend/app/models/producto_categoria.py` (unique constraint), `backend/app/models/producto_ingrediente.py` (unique constraint), `backend/alembic/versions/` (nueva migración), `backend/tests/api/test_productos.py` (nuevos tests)
- **Dependencias**: Requiere products-catalog-crud (archivado) — los modelos M2M ya existen
