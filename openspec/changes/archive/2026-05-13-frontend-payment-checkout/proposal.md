## Why

El backend de pagos con MercadoPago ya está implementado (`payment-core`). Pero el usuario no tiene forma de pagar: no existe pantalla de checkout, no hay formulario de tarjeta, ni feedback visual post-pago. Sin este cambio, el flujo de compra termina cuando el pedido se crea — el cliente no puede completar el pago.

Este cambio implementa toda la UI de checkout y pagos: desde la pantalla de revisión del pedido, pasando por el formulario de pago con MercadoPago.js, hasta la confirmación post-pago.

## What Changes

- Crear página `CheckoutPage` como punto de entrada al pago (resumen del pedido + selección de método de pago)
- Crear componente `CardPaymentForm` con integración del SDK MercadoPago.js para tokenización de tarjetas (PCI SAQ-A: los datos nunca tocan nuestro servidor)
- Crear hook `usePayment` que coordina el paymentStore con la API de pagos (POST /pagos/crear, GET /pagos/{pedido_id})
- Agregar polling de estado de pago post-checkout (consulta cada 5s si el webhook ya procesó el pago)
- Crear página `OrderConfirmationPage` con feedback visual de resultado del pago (aprobado/rechazado/pendiente)
- Agregar flujo de reintento para pagos rechazados
- Conectar el flujo: CartPage → CheckoutPage → OrderConfirmationPage
- Agregar las rutas correspondientes en el router de frontend

## Capabilities

### New Capabilities
- `frontend-checkout`: UI de checkout y pagos — formulario de pago con MercadoPago.js, polling de estado, confirmación post-pago, y reintento de pagos rechazados

### Modified Capabilities
- (ninguna — el backend `payment-processing` ya está completo)

## Impact

- **Frontend**: Nueva página `CheckoutPage`, nueva página `OrderConfirmationPage`, nuevo componente `CardPaymentForm` en features/payments, nuevo hook `usePayment` en features/payments, nuevas rutas en el router
- **Dependencias**: Agregar `@mercadopago/sdk-react` al `package.json` (o usar el SDK JS directamente via CDN)
- **Backend**: Sin cambios — el backend de pagos ya está implementado y archivado
- **API**: Consume `POST /api/v1/pagos/crear` (ya implementado) y `GET /api/v1/pagos/{pedido_id}` (ya implementado)
