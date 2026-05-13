## Why

El carrito tiene store y página dedicada, pero los usuarios no pueden agregar productos desde el catálogo ni ver el carrito sin navegar a otra página. Faltan: AddToCartButton en ProductCard, CartDrawer lateral accesible desde cualquier página, badge con contador en el header, e indicador flotante.

## What Changes

- **uiStore**: cartDrawerOpen + toggle
- **CartDrawer**: Panel lateral con items, cantidades, total, link a carrito
- **AddToCartButton**: Componente + integración en ProductCard
- **AppLayout**: Cart badge en header + CartDrawer
- **Floating cart**: FAB bottom-right con contador

## Capabilities

### Modified Capabilities
- `cart-client-side`: Se agregan componentes UI overlay (drawer, badge, FAB).

## Impact

- **Frontend**: `frontend/src/shared/stores/uiStore.ts`, `frontend/src/features/cart/components/CartDrawer.tsx`, `frontend/src/features/cart/components/AddToCartButton.tsx`, `frontend/src/features/catalog/components/ProductCard.tsx`, `frontend/src/shared/components/AppLayout.tsx`
