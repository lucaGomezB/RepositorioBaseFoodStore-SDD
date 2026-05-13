## 1. Backend — Modelo y migración

- [x] 1.1 Agregar campos `stock_cantidad` (Integer, default 0) y `eliminado_en` (DateTime, nullable) al modelo `Producto`
- [x] 1.2 Crear migración Alembic para los nuevos campos

## 2. Backend — Repository (soft delete + stock)

- [x] 2.1 Implementar `soft_delete()` en `ProductoRepository` que hace UPDATE con eliminado_en = NOW()
- [x] 2.2 Modificar `get_all()` y `get_by_id()` para filtrar WHERE eliminado_en IS NULL por defecto
- [x] 2.3 Agregar parámetro `incluir_eliminados: bool = False` a `get_all()`
- [x] 2.4 Implementar `actualizar_stock()` con UPDATE atómico: `SET stock_cantidad = stock_cantidad + :delta WHERE id = :id AND (stock_cantidad + :delta) >= 0`

## 3. Backend — Service

- [x] 3.1 Actualizar `ProductoService.create()` para incluir `stock_cantidad` en la creación
- [x] 3.2 Actualizar `ProductoService.update()` para incluir todos los campos
- [x] 3.3 Implementar `ProductoService.delete()` que llama a `soft_delete()` del repository
- [x] 3.4 Implementar `ProductoService.actualizar_stock()` que valida resultado y lanza HTTPException si stock insuficiente
- [x] 3.5 Agregar filtros al `get_all()` del service: categoria_id, busqueda (nombre ILIKE), disponible

## 4. Backend — Router y roles

- [x] 4.1 Cambiar dependencias de `require_admin` a `require_roles(["ADMIN", "STOCK"])` en todos los endpoints de productos
- [x] 4.2 Agregar endpoint `PATCH /api/v1/productos/{id}/stock` que llama a service.actualizar_stock()
- [x] 4.3 Agregar query params de filtro al GET list endpoint (categoria_id, busqueda, disponible, incluir_eliminados)
- [x] 4.4 Actualizar schemas (ProductoCreate, ProductoUpdate, ProductoRead) con stock_cantidad

## 5. Backend — Tests

- [x] 5.1 Test: crear producto con stock_cantidad válido
- [x] 5.2 Test: crear producto con stock negativo devuelve 422
- [x] 5.3 Test: soft delete producto y verificar que no aparece en listado
- [x] 5.4 Test: actualizar stock atómicamente (incremento y decremento)
- [x] 5.5 Test: decrementar stock por debajo de cero es rechazado
- [x] 5.6 Test: endpoint requiere roles [ADMIN, STOCK], client recibe 403
- [x] 5.7 Test: filtros GET (categoria_id, busqueda, disponible)

## 6. Frontend — Entities

- [x] 6.1 Crear tipos TypeScript para Producto en `entities/product/model.ts`
- [x] 6.2 Crear hooks TanStack Query en `entities/product/api.ts` (useProductos, useProducto, useCreateProducto, useUpdateProducto, useDeleteProducto, useUpdateStock)
- [x] 6.3 Crear schemas de validación con Zod en `entities/product/schemas.ts`

## 7. Frontend — CRUD pages

- [x] 7.1 Crear página `pages/ProductosListPage.tsx` con tabla de productos y filtros
- [x] 7.2 Crear página `pages/ProductoFormPage.tsx` para crear/editar producto
- [x] 7.3 Implementar modal/diálogo para actualización de stock en la lista
- [x] 7.4 Agregar confirmación de soft delete con feedback visual
- [x] 7.5 Agregar las rutas al router del dashboard
