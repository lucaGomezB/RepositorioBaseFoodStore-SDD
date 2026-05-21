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
