## Context

El backend del catálogo público está listo: `GET /api/v1/catalogo/productos` con paginación `page`/`limit`, `total_count`, filtros (`busqueda`, `categoria_id`, `excluir_alergenos`) y `GET /api/v1/catalogo/productos/{id}` con detalle expandido.

El frontend tiene la capa `entities/product/` con tipos y hooks para el CRUD admin, pero no para el catálogo público. `features/catalog/` es un stub vacío. `HomePage` es un placeholder.

## Goals / Non-Goals

**Goals:**
- Crear tipos `ProductoCatalogoRead` y hooks TanStack Query para endpoints públicos
- Implementar `features/catalog/` con grid, cards, filtros, paginación, skeleton loaders
- Reemplazar HomePage placeholder con el catálogo completo
- Modal de detalle expandido con ingredientes (flag alérgeno) y categorías

**Non-Goals:**
- Páginas admin de productos (ya existen)
- Carrito de compras (changes #24/#25)
- Tests frontend (no hay framework configurado)

## Decisions

### 1. Feature-sliced: catalog feature independiente
**Decisión**: Todo el catálogo vive en `features/catalog/` con subdirectorios `components/` y `hooks/`. HomePage es un orchestrator liviano.

**Razón**: Sigue la arquitectura FSD del proyecto. Separación clara de concerns. Reutilizable.

### 2. TanStack Query para datos del catálogo
**Decisión**: Hooks `useCatalogoProductos()` y `useCatalogoProducto()` usando TanStack Query con los endpoints `/catalogo/productos/`.

**Razón**: Consistente con el resto del frontend. Evita duplicar estado de servidor en Zustand.

### 3. useDebounce para búsqueda
**Decisión**: Hook `useDebounce` que retrasa 300ms la llamada a la API mientras el usuario escribe.

**Razón**: Evita llamadas innecesarias al backend. UX fluida.

### 4. Grid responsive con Tailwind
**Decisión**: `grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4` con cards de igual altura.

**Razón**: Tailwind ya está en el proyecto. Responsive sin librerías adicionales.

## Risks / Trade-offs

- **Riesgo**: Sin tests frontend, los cambios pueden regresionar.
  → **Mitigación**: Aceptado por ahora. Se puede agregar testing en change futuro.
- **Riesgo**: HomePage se vuelve muy grande si no se delega bien en features/.
  → **Mitigación**: HomePage solo orquesta. Toda la lógica vive en features/catalog/.
