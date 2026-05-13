## Why

El modulo de pedidos es el core del sistema. Sin el, los clientes no pueden confirmar su carrito ni avanzar al pago. Es el change mas complejo del proyecto: requiere modelo de datos, FSM, snapshots, validacion atomica de stock y UoW.

## What Changes

- EstadoPedido: agregar codigo (PK), orden, es_terminal + migracion
- Nuevos modelos: Pedido, DetallePedido, HistorialEstadoPedido
- Service: creacion atomica con UoW, FSM, validacion stock (SELECT FOR UPDATE), snapshots
- Router: POST /pedidos, GET /pedidos/{id}
- Tests: creacion, stock, snapshots, FSM

## Capabilities

### New Capabilities
- `orders-creation-fsm`: Creacion atomica de pedidos con maquina de estados y snapshots.

## Impact

- **Backend**: Models (estado_pedido, pedido, detalle_pedido, historial_estado), schemas, service, repository, router, migracion
