## ADDED Requirements

### Requirement: Backend expone WebSocket para el KDS
El backend SHALL exponer un endpoint WebSocket `WS /api/v1/cocina/ws?token=<JWT>` que permita a los clientes autorizados (roles COCINA, PEDIDOS, ADMIN) recibir eventos en tiempo real sobre cambios de estado de pedidos en fase de cocina.

#### Scenario: Handshake exitoso con JWT válido
- **WHEN** un cliente abre conexión WebSocket con token JWT válido de rol COCINA
- **THEN** el handshake SHALL ser aceptado y la conexión registrada

#### Scenario: Handshake rechazado sin token
- **WHEN** un cliente abre conexión WebSocket sin token JWT
- **THEN** el handshake SHALL ser rechazado con código 4001

#### Scenario: Handshake rechazado con rol no autorizado
- **WHEN** un cliente con rol CLIENT abre conexión WebSocket
- **THEN** el handshake SHALL ser rechazado con código 4003

### Requirement: Evento PEDIDO_CONFIRMADO se emite al aprobar pago
Cuando un pedido transiciona de PENDIENTE a CONFIRMADO (por pago aprobado), el backend SHALL emitir un evento `PEDIDO_CONFIRMADO` a todas las conexiones WebSocket activas. El evento SHALL incluir pedido_id y los datos necesarios para mostrar la tarjeta.

#### Scenario: Nuevo pedido aparece en KDS sin recargar
- **WHEN** un pago es aprobado y el pedido pasa a CONFIRMADO
- **THEN** el backend emite PEDIDO_CONFIRMADO
- **THEN** el KDS agrega una tarjeta nueva en "Por preparar" sin recargar la página

#### Scenario: Sin pantallas conectadas
- **WHEN** no hay conexiones WebSocket activas al emitir PEDIDO_CONFIRMADO
- **THEN** el evento se descarta sin error (best-effort)

### Requirement: Evento PEDIDO_EN_PREPARACION se emite al iniciar preparación
Cuando un cocinero inicia la preparación de un pedido (CONFIRMADO → EN_PREPARACION), el backend SHALL emitir `PEDIDO_EN_PREPARACION` para que la tarjeta se mueva de columna en todas las pantallas.

#### Scenario: Tarjeta se mueve a "En preparación"
- **WHEN** un cocinero inicia preparación de un pedido
- **THEN** el backend emite PEDIDO_EN_PREPARACION
- **THEN** la tarjeta se mueve a la columna "En preparación" en todos los KDS conectados

### Requirement: Evento PEDIDO_EN_CAMINO se emite al terminar preparación
Cuando un cocinero marca un pedido como terminado (EN_PREPARACION → EN_CAMINO), el backend SHALL emitir `PEDIDO_EN_CAMINO` para que la tarjeta desaparezca del KDS.

#### Scenario: Tarjeta desaparece del KDS
- **WHEN** un cocinero marca un pedido como terminado
- **THEN** el backend emite PEDIDO_EN_CAMINO
- **THEN** la tarjeta desaparece del KDS en todas las pantallas conectadas

### Requirement: Evento PEDIDO_CANCELADO se emite al cancelar en fase cocina
Cuando un pedido en CONFIRMADO o EN_PREPARACION es cancelado, el backend SHALL emitir `PEDIDO_CANCELADO` para que la tarjeta desaparezca del KDS.

#### Scenario: Cancelación remueve tarjeta del KDS
- **WHEN** un pedido en CONFIRMADO o EN_PREPARACION es cancelado
- **THEN** el backend emite PEDIDO_CANCELADO
- **THEN** la tarjeta desaparece del KDS

### Requirement: Gestor de conexiones en proceso (pub/sub)
El backend SHALL implementar un ConnectionManager que mantenga un conjunto de conexiones WebSocket activas en memoria, protegido para concurrencia con asyncio. El manager SHALL permitir broadcast de mensajes JSON a todas las conexiones activas.

#### Scenario: Broadcast a múltiples conexiones
- **WHEN** se publica un evento
- **THEN** todas las conexiones activas registradas reciben el mensaje

#### Scenario: Conexión caída no afecta broadcast
- **WHEN** una conexión se cierra inesperadamente durante un broadcast
- **THEN** las demás conexiones reciben el mensaje sin error
- **THEN** la conexión caída se elimina del gestor

### Requirement: Cliente WebSocket reconecta automáticamente
El frontend SHALL intentar reconectar automáticamente al WebSocket cuando se detecta una desconexión, con backoff exponencial (1s, 2s, 4s, max 30s).

#### Scenario: Reconexión automática
- **WHEN** el WebSocket se desconecta
- **THEN** el cliente intenta reconectar con backoff exponencial

### Requirement: Fallback a polling cuando WebSocket no está disponible
Si el WebSocket no puede conectarse o se desconecta, el frontend SHALL activar un modo de polling que haga GET /api/v1/cocina/pedidos cada 30 segundos. Al reconectar el WebSocket, SHALL volver al modo push y refrescar el estado.

#### Scenario: Polling activo durante desconexión
- **WHEN** el WebSocket está desconectado
- **THEN** el KDS muestra indicador "sin conexión en vivo"
- **THEN** el KDS hace polling cada 30s

#### Scenario: Vuelta a push al reconectar
- **WHEN** el WebSocket reconecta exitosamente
- **THEN** el KDS desactiva el polling
- **THEN** el KDS refresca el estado completo
- **THEN** vuelve al modo push
