## Why

El módulo de pagos ya tiene toda la lógica para integrarse con MercadoPago real, pero solo funciona con el endpoint mock. Para poder procesar pagos reales con tarjetas Visa/Mastercard de prueba necesitamos:

1. Una URL pública (`ngrok`) para que MercadoPago pueda notificar al webhook
2. La configuración del webhook en el dashboard de MP con su firma secreta
3. Rate limiting en el webhook (endpoint público, sin auth)
4. Procesamiento asíncrono real para no bloquear la respuesta a MP

Este change habilita la integración real con MercadoPago vía ngrok para desarrollo.

## What Changes

- **`APP_URL` en `.env`**: se documenta cómo configurarlo con la URL de ngrok
- **Rate limiting**: se agrega slowapi `@limiter` al endpoint público `POST /api/v1/pagos/webhook`
- **Procesamiento asíncrono**: la lógica pesada del webhook se mueve a `BackgroundTasks`, respondiendo 200 inmediato
- **Logging**: se agrega logging estructurado en cada paso del webhook
- **Documentación**: guías para setup de ngrok y configuración del dashboard de MP

## Capabilities

### New Capabilities
Ninguna — solo infraestructura y configuración sobre funcionalidad existente.

### Modified Capabilities
- `payment-processing`: Webhook rate limiting, procesamiento asíncrono vía BackgroundTasks, logging

## Impact

- `backend/app/api/pagos.py`: Agregar `@limiter` al webhook, mover lógica a `BackgroundTasks`
- `backend/app/domain/pagos/service.py`: Sin cambios (la lógica ya está)
- `docs/NGROK_SETUP.md`: Nuevo archivo guía (excluído de git)
- `.env.example`: Agregar `APP_URL` con comentario de ngrok
- `backend/tests/api/test_pagos.py`: Tests para rate limiting del webhook
