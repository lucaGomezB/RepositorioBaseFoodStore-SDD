## Context

Pedidos es greenfield. Existen los patrones base (UoW, BaseRepository) y el seed de 6 estados. EstadoPedido modelo existe pero incompleto.

## Goals / Non-Goals

**Goals:**
- Modelo EstadoPedido completo (codigo PK, orden, es_terminal)
- Modelos Pedido, DetallePedido, HistorialEstadoPedido
- Creacion atomica con UoW (snapshots de precio, direccion, exclusiones)
- Validacion de stock con SELECT FOR UPDATE
- FSM con mapa de transiciones
- POST /pedidos y GET /pedidos/{id}

**Non-Goals:**
- Transiciones de estado (change #27)
- Webhooks de pago (change #31)

## Decisions

### 1. EstadoPedido con codigo VARCHAR como PK
**Decision**: Usar codigo VARCHAR (PENDIENTE, CONFIRMADO, etc.) como PK natural en vez de ID numerico.

**Razon**: El seed ya tiene 6 estados con IDs estables. El codigo es mas legible en logs y debugging. s,,

### 2. Snapshots en columnas del Pedido
**Decision**: Direccion snapshot como columnas separadas (direccion_calle, direccion_numero, etc.) en vez de JSON.

**Razon**: Tipado fuerte, consultable, sin parsing.

### 3. FSM con diccionario de transiciones
**Decision**: Mapa { desde: [hacia, ...] } en el service, validado antes de cada transicion.

**Razon**: Simple, testeable, sin dependencias externas.

### 4. SELECT FOR UPDATE para stock
**Decision**: Dentro de la transaccion UoW, hacer SELECT ... FOR UPDATE sobre cada producto antes de insertar detalles.

**Razon**: Evita race conditions. RN-PE04 lo exige.

## Risks

- Migracion de EstadoPedido: la tabla ya tiene datos de seed. Hay que modificar la tabla con ALTER, no recrearla.
- El UoW actual usa session.commit() al salir del context manager. La creacion del pedido debe ser una sola transaccion atomica.
