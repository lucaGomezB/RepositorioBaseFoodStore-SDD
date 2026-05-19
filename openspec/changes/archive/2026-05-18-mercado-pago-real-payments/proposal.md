## Why

Ya contamos con cuentas de prueba de MercadoPago (Access Token + Public Key). El proyecto tiene toda la infraestructura backend para pagos reales (endpoint `POST /pagos/crear`, webhook IPN, idempotency), pero el frontend de checkout sigue usando el flujo mock (`POST /pagos/mock`) con un formulario de tarjeta simulado. Es momento de conectar el frontend a MercadoPago real para que el flujo de pago completo funcione de extremo a extremo.

## What Changes

- **Frontend — PagoPage**: Reemplazar el formulario de tarjeta mock (`validarTarjeta` + inputs manuales) por el componente `CardPaymentForm` que ya existe y usa `@mercadopago/sdk-react` para tokenizar la tarjeta sin exponer datos al servidor (PCI SAQ-A).
- **Frontend — Flujo de pago**: Cambiar de `POST /pagos/mock` a `POST /pagos/crear` enviando el `card_token` generado por MercadoPago.js.
- **Frontend — Confirmación**: Agregar polling del estado del pago (`GET /pagos/{pedido_id}`) mientras llega el webhook de MP, mostrando estados intermedios (pendiente, aprobado, rechazado).
- **Frontend — Reintento**: Si el pago es rechazado, permitir reintentar con nuevos datos de tarjeta.
- **Config**: Completar las 4 variables de entorno con las credenciales reales de MP (2 en backend, 1 en frontend, 1 webhook secret).
- **Mock se mantiene**: El endpoint `POST /pagos/mock` y su flujo queda disponible para desarrollo local sin conexión a MP.

## Capabilities

### New Capabilities
- `mercado-pago-checkout`: Integración del checkout con MercadoPago real — tokenización de tarjeta en el frontend, creación de pago contra MP, polling de estado, reintento ante rechazo.

### Modified Capabilities
- `payment-processing`: Se actualizan los escenarios del spec para reflejar que el flujo real ya está operativo (no mock). Los requerimientos existentes ya cubren el flujo real, solo se agrega explícitamente que el mock es una alternativa para desarrollo.
- `frontend-checkout`: Se reemplaza el flujo mock en PagoPage por el flujo real con `CardPaymentForm`, sin cambios en los requerimientos del spec (ya describen el flujo real).

## Impact

- **Frontend**: `PagoPage.tsx` — reemplazar formulario mock + cambiar endpoint; `ConfirmacionPage.tsx` — agregar polling de estado de pago.
- **Config**: `backend/.env` (3 vars) + `frontend/.env.local` (1 var).
- **No breaking**: El flujo mock sigue funcionando para desarrollo; el endpoint `/pagos/mock` no se elimina.
