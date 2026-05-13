## Why

El CRUD de productos (products-catalog-crud) y las relaciones M2M (products-associations) ya están implementados. Pero el catálogo público que los clientes ven en la tienda no está completo: falta filtro por alérgenos, el detalle de producto no muestra ingredientes ni categorías, la paginación no tiene conteo total, y se revela la cantidad exacta de stock. Las US-018, US-019 y US-023 lo requieren.

## What Changes

- **GET /api/v1/productos — Filtro excluir_alergenos**: Agregar query param `excluir_alergenos` que recibe IDs de ingredientes separados por coma y excluye productos que los contengan (US-023).
- **GET /api/v1/productos — Paginación con conteo**: Agregar `page`/`limit` como alias de `skip`/`limit` más `total_count` en la respuesta para que el frontend pueda paginar correctamente (US-018).
- **GET /api/v1/productos — Default disponible**: Para usuarios no autenticados, filtrar solo `disponible=true` por defecto (comportamiento de catálogo público).
- **GET /api/v1/productos/{id} — Detalle expandido**: Incluir ingredientes con flag de alérgeno, categorías, y stock como booleano (no cantidad exacta) (US-019).
- **Tests**: Tests para acceso público, filtro alérgenos, detalle expandido, paginación.

## Capabilities

### Modified Capabilities
- `products-catalog`: Se modifican los requirements de listado público y detalle de producto para incluir filtro por alérgenos, paginación con conteo, detalle expandido con ingredientes/categorías, y ocultar stock exacto.

## Impact

- **Backend**: `backend/app/api/productos.py` (filtro excluir_alergenos, paginación), `backend/app/core/services/producto.py` (lógica de filtros y detalle expandido), `backend/app/core/repositories/producto.py` (query con NOT EXISTS), `backend/app/core/schemas/producto.py` (nuevo schema ProductoCatalogoRead con stock booleano, ingredientes, categorías), `backend/tests/api/test_productos.py` (nuevos tests)
- **Dependencias**: products-catalog-crud, products-associations
