## 1. Modelos y migraciones

- [x] 1.1 Actualizar EstadoPedido: agregar codigo VARCHAR PK, orden INT, es_terminal BOOL + migracion
- [x] 1.2 Crear modelo Pedido con FK a usuario, estado, direccion snapshot (calle, numero, piso, ciudad, cp), total, costo_envio, created_at
- [x] 1.3 Crear modelo DetallePedido con FK a pedido, producto, nombre_snapshot, precio_snapshot, cantidad, exclusiones (ARRAY), subtotal
- [x] 1.4 Crear modelo HistorialEstadoPedido append-only con FK a pedido, estado_desde (nullable), estado_hacia, motivo (nullable), created_at
- [x] 1.5 Migracion Alembic para tablas nuevas

## 2. Repository

- [x] 2.1 Crear OrderRepository con métodos CRUD + get_by_usuario
- [x] 2.2 Implementar verificación de stock con SELECT FOR UPDATE

## 3. Service + FSM

- [x] 3.1 Implementar crear_pedido con UoW: validar stock, snapshots precio/direccion/exclusiones, calcular total, insertar Pedido + Detalles + HistorialInicial, vaciar carrito
- [x] 3.2 Implementar FSM: mapa de transiciones, validar_transicion()

## 4. Router

- [x] 4.1 Crear api/pedidos.py con POST /pedidos y GET /pedidos/{id}
- [x] 4.2 Registrar router

## 5. Tests

- [x] 5.1 Test: crear pedido exitosamente
- [x] 5.2 Test: stock insuficiente rechaza pedido
- [x] 5.3 Test: snapshot de precio y direccion
- [x] 5.4 Test: exclusiones se almacenan como INTEGER[]
- [x] 5.5 Test: historial registra estado inicial PENDIENTE
