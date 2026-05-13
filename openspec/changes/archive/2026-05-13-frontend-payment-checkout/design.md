## Context

El backend de pagos ya está implementado y archivado (`payment-core`). El frontend tiene:

- `paymentStore.ts` en `shared/stores/` — store Zustand con estado del flujo de pago
- `features/payments/__init__.py` — carpeta vacía (scaffold)
- `features/cart/` — feature de carrito con componentes (CartDrawer, etc.)
- `pages/CartPage.tsx` — página del carrito
- `pages/PedidoDetailPage.tsx` — detalle de pedido (donde se puede ver estado post-pago)

NO existe todavía:
- Página de checkout / pago
- Formulario de tarjeta con MercadoPago.js
- Hook personalizado para la API de pagos
- Página de confirmación post-pago
- Polling de estado de pago
- Integración del SDK MercadoPago.js

## Goals / Non-Goals

**Goals:**
- Crear `CheckoutPage` como paso posterior al carrito: resumen del pedido + formulario de pago
- Crear `CardPaymentForm` con tokenización vía MercadoPago.js (PCI SAQ-A)
- Crear hook `usePayment` que consume `POST /api/v1/pagos/crear` y `GET /api/v1/pagos/{pedido_id}`
- Implementar polling de estado de pago (cada 5s hasta 2min, luego mostrar "pendiente")
- Crear `OrderConfirmationPage` con feedback visual: aprobado (✅), rechazado (❌), pendiente (⏳)
- Flujo de reintento: si el pago fue rechazado, permitir volver al checkout con nuevo card_token
- Integrar `@mercadopago/sdk-react` para tokenización segura
- Agregar rutas: `/checkout` y `/pedidos/{id}/confirmacion`
- Conectar `CartPage` → `CheckoutPage` → `OrderConfirmationPage`

**Non-Goals:**
- Página de configuración del sistema (US-060, Sprint 8)
- UI de administración de pagos (el admin no necesita pagar)
- Reintento de pago con cambio de método (solo reintentar con datos nuevos del mismo método)
- Pago con otros medios (solo tarjeta vía MercadoPago)

## Decisions

### 1. Flujo de navegación

```
CartPage → [Crear Pedido] → CheckoutPage → [Pagar] → OrderConfirmationPage
                                                              │
                                                     ┌───────┴────────┐
                                                     ▼                ▼
                                                Aprobado      Rechazado → CheckoutPage (retry)
                                                     │
                                                     ▼
                                             PedidoDetailPage
```

1. Usuario en `CartPage` → hace clic en "Ir a pagar"
2. Se llama a `POST /api/v1/pedidos/` para crear el pedido
3. Redirige a `CheckoutPage` con el `pedido_id`
4. En `CheckoutPage`: resumen del pedido + formulario `CardPaymentForm`
5. Usuario ingresa datos de tarjeta → SDK MercadoPago.js genera `card_token`
6. Se llama a `POST /api/v1/pagos/crear` con `pedido_id` y `card_token`
7. Redirige a `OrderConfirmationPage`
8. `OrderConfirmationPage` hace polling a `GET /api/v1/pagos/{pedido_id}` cada 5s
9. Si `mp_status = "approved"` → pantalla de éxito con link al detalle
10. Si `mp_status = "rejected"` → pantalla de error con botón "Reintentar"

### 2. Componentes

```
features/payments/
├── api.ts                    ← Funciones para consumir endpoints de pagos
├── hooks/
│   └── usePayment.ts         ← Hook con polling + estado del pago
├── components/
│   ├── CardPaymentForm.tsx   ← Formulario con integración MercadoPago.js
│   └── PaymentStatusCard.tsx ← Badge/tarjeta de estado del pago
└── index.ts                  ← Re-exportaciones
```

### 3. Integración MercadoPago.js

Se usa `@mercadopago/sdk-react` (o el script CDN directamente) para generar el `card_token` en el navegador. El SDK se inicializa con `VITE_MP_PUBLIC_KEY` (variable de entorno) al montar el componente:

```tsx
import { initMercadoPago, CardPayment } from '@mercadopago/sdk-react';

initMercadoPago(import.meta.env.VITE_MP_PUBLIC_KEY);
```

El `CardPayment` de MercadoPago.js renderiza un iframe seguro donde el usuario ingresa los datos de la tarjeta. El SDK retorna un `card_token` que se envía al backend. Los datos sensibles NUNCA tocan nuestro servidor (PCI SAQ-A).

### 4. Polling de estado

Después de crear el pago, el frontend no sabe si el webhook de MP ya procesó la notificación. Por eso se implementa polling:

- Intervalo: 5 segundos
- Timeout: 2 minutos (si después de 2 min el pago sigue pending, mostrar "Pago en proceso, vuelve más tarde")
- Cada tick: `GET /api/v1/pagos/{pedido_id}`
- Si `mp_status = "approved"` o `"rejected"` → detener polling y mostrar resultado
- Si `mp_status = "pending"` → seguir polling

### 5. Store Zustand existente

El `paymentStore.ts` ya tiene toda la estructura necesaria. Se usa directamente sin modificaciones. El hook `usePayment` sincroniza el store con las llamadas API.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| **Card token expira (7 días)** | El flujo checkout → pago es inmediato, no debería expirar. Si expira, se captura el error y se pide regenerar. |
| **Webhook lento**: MP puede tardar en enviar el webhook | Polling cada 5s con timeout de 2min. Si expira, mostrar "Pago en proceso". |
| **SDK MercadoPago.js no carga** (CDN caído) | Cargar SDK como dependencia npm (`@mercadopago/sdk-react`) en vez de CDN para mejor disponibilidad. |
| **Usuario cierra el navegador antes del resultado** | El paymentStore persiste `preferenceId` y `orderId`. Al volver a OrderConfirmationPage retoma el polling. |
| **Doble clic en "Pagar"** | Deshabilitar el botón después del primer clic hasta recibir respuesta. |
