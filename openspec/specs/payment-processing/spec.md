## MODIFIED Requirements

### Requirement: Tabla Pago cumple con estructura definida
La tabla `pagos` DEBE contener los campos definidos en el ERD v5 con sus restricciones correspondientes.

#### Scenario: Estructura de tabla Pago (timezone aware)
- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** existe la tabla `pagos` con columnas: `id`, `pedido_id`, `mp_payment_id`, `mp_status`, `external_reference`, `idempotency_key`, `card_token` (nullable), `status_detail`, `created_at`, `updated_at`
- **THEN** `created_at` y `updated_at` almacenan datetimes con timezone (no naive)

### Requirement: card_token no se persiste
El sistema NO DEBE persistir el `card_token` en la tabla `pagos` después de creado el pago.

#### Scenario: card_token no se guarda en BD
- **WHEN** se crea un pago exitosamente
- **THEN** el campo `card_token` en el registro `Pago` es NULL, incluso si se proporcionó un token en el request

### Requirement: Sistema mantiene endpoint mock como alternativa de desarrollo
El sistema DEBE mantener el endpoint `POST /api/v1/pagos/mock` como alternativa para desarrollo y testing sin conexión a MercadoPago. Este endpoint aprueba el pago inmediatamente sin llamar a la API de MP.

#### Scenario: Pago mock exitoso
- **WHEN** se envía `POST /api/v1/pagos/mock` con `pedido_id` válido
- **THEN** el sistema crea un pago con `mp_status = "approved"` sin llamar a MercadoPago
- **THEN** el pedido se transiciona a CONFIRMADO inmediatamente
- **THEN** el sistema retorna HTTP 201 con los datos del pago mock
- **THEN** se decrementa el stock de los productos del pedido
