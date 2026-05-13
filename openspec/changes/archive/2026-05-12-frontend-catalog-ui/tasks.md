## 1. Entities — Tipos y hooks para catálogo público

- [x] 1.1 Agregar tipos `ProductoCatalogoRead`, `CatalogoResponse`, `CatalogoFilters` en `entities/product/model.ts`
- [x] 1.2 Crear hooks `useCatalogoProductos(filters)` y `useCatalogoProducto(id)` en `entities/product/api.ts`

## 2. Features — Catalog components

- [x] 2.1 Crear `ProductCard.tsx` con imagen, nombre, precio, hay_stock badge, categorías chips
- [x] 2.2 Crear `ProductGrid.tsx` con grid responsive y mapeo de ProductCard
- [x] 2.3 Crear `SkeletonCard.tsx` con skeleton loader animado (pulse)
- [x] 2.4 Crear `CatalogFilters.tsx` con input de búsqueda y select de categoría
- [x] 2.5 Crear `CatalogPagination.tsx` con page numbers y "Mostrando X-Y de Z"
- [x] 2.6 Crear `ProductDetailModal.tsx` con detalle expandido, ingredientes (⚠️ alérgenos), categorías

## 3. Features — Catalog hooks

- [x] 3.1 Crear `useDebounce.ts` hook para retrasar búsqueda 300ms
- [x] 3.2 Crear `useCatalogFilters.ts` hook con estado de filtros + page

## 4. Pages — HomePage

- [x] 4.1 Reemplazar HomePage.tsx placeholder con el catálogo completo (ProductGrid + CatalogFilters + CatalogPagination + ProductDetailModal)
- [x] 4.2 Verificar que Sidebar ya apunta a "/" para Catálogo
