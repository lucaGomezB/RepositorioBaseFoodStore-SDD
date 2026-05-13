## Why

El backend del catálogo público (products-public-catalog) ya está implementado y archivado. Pero los clientes no tienen interfaz para ver los productos. La HomePage actual es un placeholder "Bienvenido a Food Store". Las US-018, US-019 y US-023 requieren que los clientes puedan navegar el catálogo, buscar productos, filtrar y ver detalles.

## What Changes

- **entities/product/**: Agregar tipos para `ProductoCatalogoRead`, `CatalogoResponse`, y hooks TanStack Query para los endpoints públicos `/catalogo/productos/`
- **features/catalog/**: Implementar el feature de catálogo completo: ProductGrid, ProductCard, CatalogFilters (búsqueda con debounce, categoría, alérgenos), CatalogPagination, SkeletonCard
- **pages/HomePage**: Reemplazar placeholder con el catálogo completo
- **shared/components/**: Crear componentes reutilizables si es necesario

## Capabilities

### New Capabilities
- `frontend-catalog-ui`: Interfaz de catálogo público de productos con grid, filtros, paginación y detalle expandido.

## Impact

- **Frontend**: `frontend/src/entities/product/model.ts` (nuevos tipos), `frontend/src/entities/product/api.ts` (nuevos hooks), `frontend/src/features/catalog/` (nuevo feature completo), `frontend/src/pages/HomePage.tsx` (reemplazar), `frontend/src/shared/components/` (posibles nuevos componentes)
