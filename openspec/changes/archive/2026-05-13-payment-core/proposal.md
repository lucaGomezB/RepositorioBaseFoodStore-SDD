## Why

Food Store requiere procesar pagos a través de MercadoPago para que los clientes puedan pagar sus pedidos de forma segura. Actualmente los pedidos se crean en estado PENDIENTE pero no existe ningún mecanismo para procesar el pago ni actualizar el estado del pedido cuando el pago es aprobado. Sin esta funcionalidad, el sistema no puede completar el ciclo de compra.

Este cambio implementa el core backend de pagos: modelo de datos, integración con MercadoPago SDK, y API endpoints para crear pagos y consultar su estado.

## What Changes

- Crear modelo `Pago` en base de datos con migración Alembic
- Crear schemas Pydantic para pagos (request/response)
- Crear repositorio de pagos (`PagoRepository`)
- Crear servicio de pagos con integración MercadoPago SDK (`PagoService`)
- Implementar endpoint `POST /api/v1/pagos/crear` — crear pago en MercadoPago y registrar en BD
- Implementar endpoint `GET /api/v1/pagos/{pedido_id}` — consultar pago de un pedido
- Implementar endpoint `POST /api/v1/pagos/webhook` — recibir notificaciones IPN de MercadoPago
- Configurar variables de entorno para MercadoPago (MP_ACCESS_TOKEN, MP_PUBLIC_KEY, MP_NOTIFICATION_URL)
- Agregar dependencia `mercadopago` SDK al backend
- Registrar router de pagos en `main.py`

## Capabilities

### New Capabilities
- `payment-processing`: Core backend de pagos con integración MercadoPago — modelo Pago, creación de pagos, consulta de estado, y webhook IPN

### Modified Capabilities
- `infrastructure-setup`: Agregar variables de entorno MP y dependencia SDK

## Impact

- **Backend**: Nuevo módulo `app/modules/pagos/` con model, schemas, repository, service, router. Nuevo modelo `Pago` con tabla en BD. Nueva migración Alembic. Nuevo router registrado en `/api/v1/pagos`.
- **Dependencias**: Agregar `mercadopago` al `requirements.txt`
- **Configuración**: 3 nuevas variables de entorno: `MP_ACCESS_TOKEN`, `MP_PUBLIC_KEY`, `MP_NOTIFICATION_URL`
- **Frontend**: No requiere cambios inmediatos (el `paymentStore.ts` ya existe). El frontend se integrará en un cambio posterior.
