## Why

El FSM existe en codigo pero no hay endpoint para transicionar estados. Sin esto, los pedidos quedan siempre en PENDIENTE. Ademas falta la cancelacion con restauracion de stock y el registro de usuario en el historial.

## What Changes

- HistorialEstadoPedido: agregar usuario_id + migracion
- TRANSICIONES: EN_PREP -> EN_PREPARACION (consistente con seed)
- Service: transicionar_estado(), cancelar_pedido() con restauro stock
- Router: PATCH /pedidos/{id}/estado
- Tests: transiciones, cancelacion, stock restauro, FSM validation

## Capabilities

### Modified Capabilities
- `orders-creation-fsm`: Se agregan endpoints de transicion de estados, cancelacion y auditoria.

## Impact

- **Backend**: models/historial_estado_pedido.py, core/services/pedido.py, api/pedidos.py, migracion
