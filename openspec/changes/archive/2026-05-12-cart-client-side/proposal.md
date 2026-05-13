## Why

El carrito de compras es el paso previo a los pedidos. Sin carrito, los clientes no pueden seleccionar productos ni personalizarlos (excluir ingredientes). El cartStore existe pero tiene tipos incorrectos. No hay UI de carrito en el frontend.

## What Changes

- **cartStore**: Fix CartItem.exclusiones (number[]), addItem con exclusiones, addExclusion/removeExclusion, getItem()
- **features/cart/**: CartItemRow, CartSummary, IngredientExclusionPicker, ClearCartButton
- **pages/CartPage.tsx**: Página de carrito con items + resumen
- **Sidebar + router**: Ruta /carrito

## Capabilities

### New Capabilities
- `cart-client-side`: Carrito de compras client-side con Zustand + localStorage.

## Impact

- **Frontend**: `frontend/src/shared/stores/cartStore.ts`, `frontend/src/features/cart/`, `frontend/src/pages/CartPage.tsx`, `frontend/src/app/router.tsx`, `frontend/src/shared/components/Sidebar.tsx`
