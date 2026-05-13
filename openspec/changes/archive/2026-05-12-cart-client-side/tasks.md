## 1. Fix cartStore

- [x] 1.1 Cambiar CartItem.exclusiones de `customization?: string` a `exclusiones: number[]`
- [x] 1.2 Actualizar addItem para aceptar exclusiones y usar ProductoCatalogoRead en vez de Producto
- [x] 1.3 Agregar getItem(productoId) selector
- [x] 1.4 Reemplazar updateCustomization con addExclusion/removeExclusion

## 2. Cart components

- [x] 2.1 Crear CartItemRow con nombre, precio, cantidad, exclusiones, botones +/- y eliminar
- [x] 2.2 Crear CartSummary con subtotal, total, botón "Ir a pagar" (placeholder)
- [x] 2.3 Crear ClearCartButton con confirmación modal
- [x] 2.4 Crear CartPage (o reutilizar CartPage existente)

## 3. Routing + sidebar

- [x] 3.1 Agregar ruta /carrito en router
- [x] 3.2 Agregar link "Carrito" en Sidebar (CLIENT) — **Ya existía** en Sidebar.tsx línea 20
