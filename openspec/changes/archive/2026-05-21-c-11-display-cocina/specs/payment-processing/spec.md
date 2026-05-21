## ADDED Requirements

### Requirement: Webhook de pago aprobado emite evento PEDIDO_CONFIRMADO
Cuando el webhook IPN de MercadoPago procesa un pago aprobado y transiciona el pedido de PENDIENTE a CONFIRMADO, el backend SHALL emitir un evento `PEDIDO_CONFIRMADO` a través del ConnectionManager para que las pantallas de cocina conectadas reciban el nuevo pedido en tiempo real.

#### Scenario: Evento emitido al confirmar pedido
- **WHEN** el webhook IPN recibe pago aprobado y el pedido pasa a CONFIRMADO
- **THEN** se publica el evento PEDIDO_CONFIRMADO con el pedido_id y datos del pedido
- **THEN** el KDS (si hay pantallas conectadas) recibe el evento y muestra la nueva tarjeta

#### Scenario: Evento emitido incluso sin pantallas conectadas
- **WHEN** el webhook IPN procesa pago aprobado
- **THEN** se publica PEDIDO_CONFIRMADO incluso si no hay conexiones activas (se descarta silenciosamente, best-effort)
