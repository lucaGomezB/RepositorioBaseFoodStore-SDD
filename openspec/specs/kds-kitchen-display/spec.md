## ADDED Requirements

### Requirement: KDS muestra pedidos a preparar en dos columnas
El KDS SHALL mostrar los pedidos en dos columnas: "Por preparar" (estado CONFIRMADO) y "En preparación" (estado EN_PREPARACION). Cada pedido SHALL aparecer como una tarjeta con número de pedido, ítems (nombre_snapshot × cantidad), exclusiones de personalización, y notas del cliente.

#### Scenario: Carga inicial del KDS
- **WHEN** un cocinero autenticado ingresa a /cocina
- **THEN** el frontend hace GET /api/v1/cocina/pedidos
- **THEN** se muestran dos columnas con los pedidos existentes en CONFIRMADO y EN_PREPARACION

#### Scenario: Pedido en PENDIENTE no aparece
- **WHEN** existe un pedido en estado PENDIENTE (sin pago aprobado)
- **THEN** el KDS NO muestra ese pedido

#### Scenario: Tarjeta muestra información completa
- **WHEN** el KDS muestra un pedido
- **THEN** la tarjeta contiene: número de pedido, lista de ítems con nombre_snapshot y cantidad, exclusiones de ingredientes, y notas del cliente

### Requirement: Pedidos ordenados por antigüedad ascendente
El KDS SHALL ordenar los pedidos por antigüedad ascendente, usando el created_at del HistorialEstadoPedido cuando el pedido entró a estado CONFIRMADO.

#### Scenario: Orden correcto de pedidos
- **WHEN** existen múltiples pedidos en CONFIRMADO
- **THEN** se ordenan del más antiguo al más reciente según su tiempo de entrada a CONFIRMADO

### Requirement: Cocinero puede iniciar preparación de un pedido
El cocinero SHALL poder marcar un pedido en CONFIRMADO como "En preparación" mediante un botón en la tarjeta. Esto transiciona el pedido a EN_PREPARACION, registra el evento en HistorialEstadoPedido, y mueve la tarjeta de columna en todas las pantallas conectadas.

#### Scenario: Iniciar preparación exitosamente
- **WHEN** el cocinero presiona "Iniciar preparación" en un pedido CONFIRMADO
- **THEN** el backend transiciona a EN_PREPARACION
- **THEN** la tarjeta se mueve de "Por preparar" a "En preparación" en todas las pantallas
- **THEN** se registra en HistorialEstadoPedido con usuario_id del cocinero

#### Scenario: Intento de transición inválida
- **WHEN** un cocinero intenta iniciar preparación de un pedido que no está en CONFIRMADO
- **THEN** el backend rechaza con HTTP 400

### Requirement: Cocinero puede marcar pedido como terminado
El cocinero SHALL poder marcar un pedido en EN_PREPARACION como terminado. Esto transiciona a EN_CAMINO, registra el evento, y la tarjeta desaparece del KDS.

#### Scenario: Marcar terminado exitosamente
- **WHEN** el cocinero presiona "Listo" en un pedido EN_PREPARACION
- **THEN** el backend transiciona a EN_CAMINO
- **THEN** la tarjeta desaparece del KDS en todas las pantallas conectadas
- **THEN** se registra en HistorialEstadoPedido con usuario_id del cocinero

### Requirement: Timer de urgencia con umbrales visuales
El KDS SHALL mostrar un timer en cada tarjeta indicando el tiempo transcurrido desde que el pedido entró a CONFIRMADO. El timer SHALL usar tres umbrales visuales: <10 min normal, 10-20 min advertencia (naranja), >20 min urgente (rojo). El cálculo SHALL ser 100% en cliente, recalculado cada 15 segundos.

#### Scenario: Timer muestra tiempo correcto
- **WHEN** un pedido lleva 5 minutos en CONFIRMADO
- **THEN** el timer muestra "5 min" con estilo normal

#### Scenario: Umbral de advertencia
- **WHEN** un pedido lleva 15 minutos en CONFIRMADO
- **THEN** el timer se muestra en color naranja

#### Scenario: Umbral de urgencia
- **WHEN** un pedido lleva 25 minutos en CONFIRMADO
- **THEN** el timer se muestra en color rojo

### Requirement: Validación de transiciones por rol COCINA
El rol COCINA SHALL solo poder ejecutar las transiciones CONFIRMADO → EN_PREPARACION y EN_PREPARACION → EN_CAMINO. Cualquier otra transición solicitada por un cocinero SHALL retornar HTTP 403, aunque el endpoint permita el acceso por require_roles.

#### Scenario: COCINA intenta entregar pedido
- **WHEN** un usuario con rol COCINA intenta transicionar EN_CAMINO → ENTREGADO
- **THEN** el backend retorna HTTP 403

#### Scenario: COCINA cancela pedido
- **WHEN** un usuario con rol COCINA intenta cancelar un pedido
- **THEN** el backend retorna HTTP 403
