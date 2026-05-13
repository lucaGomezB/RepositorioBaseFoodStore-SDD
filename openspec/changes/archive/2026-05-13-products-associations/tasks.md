## 1. Bugfix — Dict access en service

- [x] 1.1 Corregir `add_ingrediente()` en `ProductoService` para acceder `data["ingrediente_id"]` en vez de `data.ingrediente_id`
- [x] 1.2 Corregir `add_categoria()` en `ProductoService` para acceder `data["categoria_id"]` en vez de `data.categoria_id`

## 2. Unique constraints + migración

- [x] 2.1 Agregar unique constraint compuesta `(producto_id, categoria_id)` al modelo `ProductoCategoria`
- [x] 2.2 Agregar unique constraint compuesta `(producto_id, ingrediente_id)` al modelo `ProductoIngrediente`
- [x] 2.3 Crear migración Alembic para las unique constraints

## 3. Endpoints PUT de reemplazo masivo

- [x] 3.1 Implementar `reemplazar_ingredientes()` en `ProductoService` que elimina todas las relaciones existentes e inserta las nuevas dentro de una transacción
- [x] 3.2 Implementar `reemplazar_categorias()` en `ProductoService` (misma lógica)
- [x] 3.3 Agregar endpoint `PUT /api/v1/productos/{id}/ingredientes` en el router con protección ADMIN/STOCK
- [x] 3.4 Agregar endpoint `PUT /api/v1/productos/{id}/categorias` en el router con protección ADMIN/STOCK

## 4. Tests

- [x] 4.1 Test: PUT ingredientes reemplaza correctamente
- [x] 4.2 Test: PUT categorías reemplaza correctamente
- [x] 4.3 Test: PUT con array vacío elimina todas las relaciones
- [x] 4.4 Test: PUT sobre producto inexistente devuelve 404
- [x] 4.5 Test: GET ingredientes lista relaciones
- [x] 4.6 Test: GET categorías lista relaciones
- [x] 4.7 Test: POST agregar ingrediente funciona (después del bugfix)
- [x] 4.8 Test: POST agregar categoría funciona (después del bugfix)
- [x] 4.9 Test: DELETE ingrediente funciona
- [x] 4.10 Test: DELETE categoría funciona
- [x] 4.11 Test: duplicate category returns 409 (unique constraint)
