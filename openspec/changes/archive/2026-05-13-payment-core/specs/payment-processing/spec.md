## ADDED Requirements

### Requirement: Sistema puede crear un pago en MercadoPago
El sistema DEBE permitir crear un pago en MercadoPago para un pedido en estado PENDIENTE, utilizando un card_token generado por el SDK de MercadoPago en el frontend.

#### Scenario: Creación exitosa de pago
- **WHEN** se envía `POST /api/v1/pagos/crear` con `pedido_id` válido y `card_token` válido
- **THEN** el sistema llama a la API de MercadoPago para crear el pago
- **THEN** el sistema registra un nuevo registro en la tabla `Pago` con `mp_payment_id`, `mp_status` inicial y `external_reference`
- **THEN** el sistema retorna HTTP 201 con los datos del pago creado

#### Scenario: Pedido no existe
- **WHEN** se envía `POST /api/v1/pagos/crear` con un `pedido_id` que no existe
- **THEN** el sistema retorna HTTP 404 con mensaje "Pedido no encontrado"

#### Scenario: Pedido no está en PENDIENTE
- **WHEN** se envía `POST /api/v1/pagos/crear` para un pedido que no está en estado PENDIENTE
- **THEN** el sistema retorna HTTP 409 con mensaje "El pedido no está en estado PENDIENTE"

#### Scenario: Idempotencia por clave duplicada
- **WHEN** se envía `POST /api/v1/pagos/crear` con un `idempotency_key` que ya fue usado
- **THEN** el sistema retorna el pago existente sin crear uno nuevo (HTTP 200 en lugar de 201)

#### Scenario: Error al crear pago en MercadoPago
- **WHEN** la API de MercadoPago retorna un error al crear el pago
- **THEN** el sistema registra el pago con `mp_status = "rejected"` y el `status_detail` del error
- **THEN** el sistema retorna HTTP 402 con mensaje descriptivo del error

---

### Requirement: Frontend puede tokenizar tarjeta sin exponer datos al servidor
La tokenización de tarjetas DEBE ocurrir exclusivamente en el navegador mediante el SDK de MercadoPago.js. Los datos sensibles de la tarjeta NUNCA deben pasar por el servidor de Food Store (PCI DSS SAQ-A).

#### Scenario: Tokenización de tarjeta
- **WHEN** el cliente ingresa los datos de su tarjeta en el formulario de pago
- **THEN** el SDK de MercadoPago.js genera un `card_token` en el navegador
- **THEN** el frontend envía SOLO el `card_token` al backend, nunca los datos de la tarjeta

---

### Requirement: Sistema puede consultar estado de un pago
El sistema DEBE permitir consultar el estado de un pago asociado a un pedido.

#### Scenario: Consulta exitosa de pago
- **WHEN** se envía `GET /api/v1/pagos/{pedido_id}` con un `pedido_id` que tiene un pago registrado
- **THEN** el sistema retorna HTTP 200 con los datos del pago: `mp_payment_id`, `mp_status`, `status_detail`, `created_at`, `updated_at`

#### Scenario: Pedido sin pagos registrados
- **WHEN** se envía `GET /api/v1/pagos/{pedido_id}` para un pedido sin pagos
- **THEN** el sistema retorna HTTP 404 con mensaje "No se encontraron pagos para este pedido"

#### Scenario: Cliente no propietario consulta pago ajeno
- **WHEN** un cliente consulta el pago de un pedido que no le pertenece
- **THEN** el sistema retorna HTTP 403 Forbidden

---

### Requirement: Sistema procesa webhook IPN de MercadoPago
El sistema DEBE procesar notificaciones IPN (Instant Payment Notification) enviadas por MercadoPago para actualizar el estado del pago y, cuando corresponda, del pedido.

#### Scenario: Webhook recibe pago aprobado
- **WHEN** se recibe `POST /api/v1/pagos/webhook` con `type = "payment"` y `data.id` válido
- **THEN** el sistema responde HTTP 200 inmediatamente (antes de procesar)
- **THEN** el sistema consulta la API de MercadoPago para verificar el estado real del pago
- **THEN** si `mp_status = "approved"`, el sistema actualiza el registro en tabla `Pago` con el nuevo estado
- **THEN** el sistema transiciona automáticamente el pedido de PENDIENTE a CONFIRMADO
- **THEN** el sistema decrementa el stock de los productos del pedido atómicamente

#### Scenario: Webhook recibe pago rechazado
- **WHEN** se recibe webhook con `mp_status = "rejected"`
- **THEN** el sistema actualiza el registro en tabla `Pago` con `mp_status = "rejected"`
- **THEN** el pedido permanece en estado PENDIENTE

#### Scenario: Webhook recibe pago pendiente
- **WHEN** se recibe webhook con `mp_status = "pending"` o `"in_process"`
- **THEN** el sistema actualiza el registro en tabla `Pago` con el estado correspondiente
- **THEN** el pedido permanece en estado PENDIENTE

#### Scenario: Webhook duplicado no causa efectos duplicados
- **WHEN** se recibe el mismo webhook dos veces (mismo `mp_payment_id` y mismo estado)
- **THEN** el sistema detecta que ya fue procesado y retorna HTTP 200 sin ejecutar cambios duplicados

#### Scenario: Firma de webhook inválida
- **WHEN** se recibe un webhook con firma inválida o sin firma
- **THEN** el sistema retorna HTTP 403 Forbidden

---

### Requirement: Sistema utiliza idempotency key para evitar cobros duplicados
Cada pago DEBE tener un `idempotency_key` UUID único generado por el backend. Si se recibe una solicitud de creación de pago con la misma `idempotency_key`, el sistema debe retornar el pago existente sin crear uno nuevo.

#### Scenario: Idempotencia en creación de pago
- **WHEN** se envía `POST /api/v1/pagos/crear` con mismo `idempotency_key` que un pago previo
- **THEN** el sistema retorna el pago existente sin crear uno nuevo
- **THEN** no se llama a la API de MercadoPago nuevamente

---

### Requirement: Tabla Pago cumple con estructura definida
La tabla `pagos` DEBE contener los campos definidos en el ERD v5 con sus restricciones correspondientes.

#### Scenario: Estructura de tabla Pago
- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** existe la tabla `pagos` con columnas: `id`, `pedido_id`, `mp_payment_id`, `mp_status`, `external_reference`, `idempotency_key`, `card_token`, `status_detail`, `created_at`, `updated_at`
- **THEN** `mp_payment_id` tiene restricción UNIQUE
- **THEN** `external_reference` tiene restricción UNIQUE
- **THEN** `idempotency_key` tiene restricción UNIQUE
- **THEN** `mp_status` tiene valor por defecto "pending"
