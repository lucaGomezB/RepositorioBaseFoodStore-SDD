## 1. Setup frontend payments feature

- [x] 1.1 Instalar `@mercadopago/sdk-react` en `frontend/package.json`
- [x] 1.2 Crear estructura de `features/payments/`: api.ts, types, hooks/usePayment.ts, components/CardPaymentForm.tsx, components/PaymentStatusCard.tsx, index.ts

## 2. API layer para pagos

- [x] 2.1 Crear `features/payments/api.ts` con funciones crearPago + obtenerPago
- [x] 2.2 Tipos TypeScript: PagoRead, CrearPagoRequest, PaymentStatus, CrearPagoResponse

## 3. Hook usePayment

- [x] 3.1 Crear `features/payments/hooks/usePayment.ts`: useCreatePayment (mutation) + usePaymentStatus (query) + helpers
- [x] 3.2 Sincronizar con paymentStore de Zustand (setOrder, setPaymentStatus)

## 4. Componente CardPaymentForm

- [x] 4.1 Crear `features/payments/components/CardPaymentForm.tsx` con SDK MercadoPago.js, tokenización PCI SAQ-A

## 5. Componente PaymentStatusCard

- [x] 5.1 Crear `features/payments/components/PaymentStatusCard.tsx` con 5 estados + acciones

## 6. Página CheckoutPage

- [x] 6.1 Crear `pages/CheckoutPage.tsx`: resumen pedido + CardPaymentForm + creación de pago

## 7. Página OrderConfirmationPage

- [x] 7.1 Crear `pages/OrderConfirmationPage.tsx`: polling 3s + PaymentStatusCard + timeout 2min

## 8. Integrar rutas y navegación

- [x] 8.1 Agregar rutas en `app/router.tsx`: /checkout + /pedidos/:id/confirmacion
- [x] 8.2 Conectar CartSummary → crear pedido → redirigir a /checkout
- [x] 8.3 OrderConfirmationPage → link a PedidoDetailPage cuando approved
