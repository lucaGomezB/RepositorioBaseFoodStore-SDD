## ADDED Requirements

### Requirement: Sistema mantiene endpoint mock como alternativa de desarrollo
El sistema DEBE mantener el endpoint `POST /api/v1/pagos/mock` como alternativa para desarrollo y testing sin conexión a MercadoPago. Este endpoint aprueba el pago inmediatamente sin llamar a la API de MP.

#### Scenario: Pago mock exitoso
- **WHEN** se envía `POST /api/v1/pagos/mock` con `pedido_id` válido
- **THEN** el sistema crea un pago con `mp_status = "approved"` sin llamar a MercadoPago
- **THEN** el pedido se transiciona a CONFIRMADO inmediatamente
- **THEN** el sistema retorna HTTP 201 con los datos del pago mock
- **THEN** se decrementa el stock de los productos del pedido
