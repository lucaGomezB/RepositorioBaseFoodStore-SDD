## MODIFIED Requirements

### Requirement: Sistema procesa webhook IPN de MercadoPago
El sistema DEBE procesar notificaciones webhook enviadas por MercadoPago para actualizar el estado del pago y, cuando corresponda, del pedido.

#### Scenario: Webhook responde 200 inmediato
- **WHEN** se recibe `POST /api/v1/pagos/webhook`
- **THEN** el sistema responde HTTP 200 inmediatamente ANTES de procesar (vía BackgroundTasks)

#### Scenario: Rate limiting en webhook
- **WHEN** se reciben más de 10 requests por minuto al webhook desde la misma IP
- **THEN** el sistema retorna HTTP 429 Too Many Requests

#### Scenario: Logging de cada paso
- **WHEN** el webhook procesa una notificación
- **THEN** se registra en logs: recepción, validación de firma, consulta a MP API, transición de estado, broadcast de evento
