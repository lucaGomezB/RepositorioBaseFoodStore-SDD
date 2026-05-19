## 1. Configurar credenciales de MercadoPago

- [x] 1.1 Completar `MERCADOPAGO_ACCESS_TOKEN` y `MERCADOPAGO_PUBLIC_KEY` en `backend/.env` con las credenciales de prueba
- [x] 1.2 Completar `VITE_MP_PUBLIC_KEY` en `frontend/.env.local` con la Public Key de prueba
- [x] 1.3 Configurar `MERCADOPAGO_WEBHOOK_SECRET` en `backend/.env` para validación de firma IPN

## 2. Refactorizar PagoPage: integrar CardPaymentForm real

- [x] 2.1 Reemplazar el formulario mock (inputs manuales + `validarTarjeta()`) por el componente `CardPaymentForm` de `@mercadopago/sdk-react`
- [x] 2.2 Conectar `onToken` de `CardPaymentForm` para obtener el `card_token` al enviar el formulario
- [x] 2.3 Cambiar el flujo de submit: crear pedido (`POST /pedidos/`) → crear pago con token (`POST /pagos/crear` con `card_token` y `pedido_id`)
- [x] 2.4 Agregar manejo de errores: si el pago falla (tarjeta rechazada), mostrar error y permitir reintento sin perder el pedido
- [x] 2.5 Implementar flag de mock: si `VITE_MP_PUBLIC_KEY` está vacía, usar formulario mock + `POST /pagos/mock`

## 3. Crear ConfirmacionPage con polling de estado

- [x] 3.1 ConfirmacionPage ya existía (`OrderConfirmationPage.tsx`) con ruta configurada
- [x] 3.2 Polling cada 3s ya implementado con `usePaymentStatus` + `queryClient.invalidateQueries`
- [x] 3.3 Estado pending con spinner ya implementado
- [x] 3.4 Pantalla de aprobado con "Ver detalle" ya implementada (vía `PaymentStatusCard`)
- [x] 3.5 Pantalla de rechazado con "Reintentar" ya implementada (vía `PaymentStatusCard`)
- [x] 3.6 Timeout de 2 minutos ya implementado
- [x] 3.7 Ruta `/pedidos/:id/confirmacion` ya existía en el router con `ProtectedRoute`

## 4. Soportar reintento de pago desde ConfirmacionPage

- [x] 4.1 PagoPage acepta `pedido_id` opcional por query param (`/pago?pedido_id={id}`)
- [x] 4.2 Si hay `pedido_id` en la URL, omite creación de pedido y va directo al pago
- [x] 4.3 Botón "Reintentar" de ConfirmacionPage redirige a `/pago?pedido_id={id}`

## 5. Verificar flujo completo

- [ ] 5.1 Verificar que el flujo real funciona con tarjetas de prueba de MP (aprobada, rechazada)
- [ ] 5.2 Verificar que el flujo mock sigue funcionando cuando no hay `VITE_MP_PUBLIC_KEY`
- [ ] 5.3 Verificar que los tests de pago existentes siguen pasando
