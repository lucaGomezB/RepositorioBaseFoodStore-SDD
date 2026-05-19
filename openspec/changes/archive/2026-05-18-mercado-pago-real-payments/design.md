## Context

El proyecto tiene integración de MercadoPago completa en el backend (SDK, endpoint `POST /pagos/crear`, webhook IPN, idempotency) y el componente `CardPaymentForm` listo en el frontend. Sin embargo, el flujo de checkout actual (`PagoPage.tsx`) usa un formulario de tarjeta mock con validación cliente-side y llama a `POST /pagos/mock` en vez de al flujo real.

Con las cuentas de prueba de MP obtenidas, podemos activar el flujo real.

## Goals / Non-Goals

**Goals:**
- Reemplazar el formulario mock de PagoPage por `CardPaymentForm` (tokenización con MP.js)
- Cambiar la llamada de `POST /pagos/mock` a `POST /pagos/crear` con `card_token`
- Crear pantalla de confirmación con polling del estado del pago
- Mantener el endpoint mock como alternativa de desarrollo

**Non-Goals:**
- No se modifica el backend de pagos (ya está completo)
- No se agregan nuevos métodos de pago (solo tarjeta por MP)
- No se implementan websockets (polling HTTP es suficiente)

## Decisions

### 1. CardPaymentForm existente se usa tal cual
El componente `CardPaymentForm` ya tokeniza la tarjeta con `@mercadopago/sdk-react` y devuelve un `card_token`. No requiere cambios — solo integrarlo en PagoPage.

### 2. Flujo: crear pedido → crear pago → polling
Secuencia:
1. PagoPage crea el pedido (`POST /pedidos/`)
2. Con el `pedido_id`, crea el pago (`POST /pagos/crear` con `card_token`)
3. Redirige a ConfirmacionPage
4. ConfirmacionPage hace polling (`GET /pagos/{pedido_id}`) cada 3s hasta obtener estado definitivo (approved/rejected) o timeout de 2min

Alternativa considerada: crear pedido y pago en una sola llamada. Descartado porque el spec actual separa ambas responsabilidades y el backend ya está así.

### 3. Mock se mantiene como feature flag
`POST /pagos/mock` y su UI alternativa (mock card form) no se eliminan. Sirven para desarrollo sin conexión a MP. Se puede activar/desactivar vía variable de entorno o query param.

### 4. Polling con react-query
Usar `@tanstack/react-query` con `refetchInterval` para el polling. Ya está en el proyecto. Si el estado es `approved` o `rejected`, se detiene el polling.

### 5. Sin cambios en backend de pagos
El backend ya implementa: `PagoService.crear_pago()` (SDK MP + idempotency), `PagoService.crear_pago_mock()`, webhook IPN con X-Signature, consulta de estado. Solo se actualizan las credenciales en `.env`.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| [MP API rate limits] Si muchas solicitudes simultáneas, MP puede rate-limit | Idempotency key evita duplicados; el backend ya maneja errores HTTP 429 |
| [Webhook lento] El webhook de MP puede demorar segundos en llegar | Polling cada 3s en ConfirmacionPage cubre el gap; timeout a los 2min |
| [Network error en MP.js] El SDK de MP.js depende de CDN externo | CardPaymentForm muestra error claro; el mock sigue disponible como fallback |
| [CardPaymentForm amount=0] El componente recibe `amount=0` fijo porque MP.js no necesita el monto para tokenizar | El monto real se envía al backend al crear el pago, no en la tokenización |
