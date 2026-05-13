## 1. Schema público ProductoCatalogoRead

- [x] 1.1 Crear schema `ProductoCatalogoRead` con `hay_stock: bool` (derivado de stock_cantidad > 0), `ingredientes: list[ProductoIngredienteRead]`, `categorias: list[ProductoCategoriaRead]`, sin exponer `stock_cantidad` ni `eliminado_en`

## 2. Repository — Filtro excluir_alergenos

- [x] 2.1 Implementar filtro `excluir_alergenos` en `get_all()` del repository usando subquery `NOT EXISTS (SELECT 1 FROM producto_ingrediente WHERE ingrediente_id IN (:ids) AND producto_id = productos.id)`

## 3. Service — Lógica pública

- [x] 3.1 Implementar `get_catalogo()` en service que usa `ProductoCatalogoRead` schema y aplica default disponible=true para anónimos
- [x] 3.2 Implementar detalle expandido en `get_by_id()` que carga ingredientes (con flag alérgeno) y categorías
- [x] 3.3 Agregar conteo total (`total_count`) a la respuesta del listado público

## 4. Router — Endpoints públicos

- [x] 4.1 Crear endpoint `GET /api/v1/catalogo/productos` con paginación page/limit, filtro excluir_alergenos, default disponible=true
- [x] 4.2 Crear endpoint `GET /api/v1/catalogo/productos/{id}` con detalle expandido y stock como booleano
- [x] 4.3 Mantener endpoints existentes para administración (sin cambios)

## 5. Tests

- [x] 5.1 Test: catálogo público solo muestra disponibles para anónimos
- [x] 5.2 Test: filtro excluir_alergenos funciona
- [x] 5.3 Test: detalle expandido incluye ingredientes y categorías
- [x] 5.4 Test: detalle no expone stock_cantidad exacta
- [x] 5.5 Test: paginación con page/limit devuelve conteo total
- [x] 5.6 Test: producto no disponible da 404 en detalle público
