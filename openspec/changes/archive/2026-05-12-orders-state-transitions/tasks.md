## 1. Modelo + migracion

- [x] 1.1 Agregar usuario_id (nullable) a HistorialEstadoPedido + migracion
- [x] 1.2 Corregir TRANSICIONES: EN_PREP -> EN_PREPARACION

## 2. Service

- [x] 2.1 Implementar transicionar_estado(): validar FSM, registrar historial, actualizar pedido
- [x] 2.2 Implementar cancelar_pedido(): si viene de CONFIRMADO, restaurar stock atomicamente

## 3. Router

- [x] 3.1 Agregar PATCH /pedidos/{id}/estado con roles ADMIN, PEDIDOS
- [x] 3.2 Agregar motivo obligatorio en cancelacion

## 4. Tests

- [x] 4.1 Test: PENDIENTE -> CANCELADO
- [x] 4.2 Test: CONFIRMADO -> CANCELADO con restauro stock
- [x] 4.3 Test: CONFIRMADO -> EN_PREPARACION
- [x] 4.4 Test: transicion invalida rechazada
- [x] 4.5 Test: cancelacion sin motivo rechazada
- [x] 4.6 Test: historial registra usuario
