## ADDED Requirements

### Requirement: Cliente puede pagar con tarjeta mediante MercadoPago.js
El sistema DEBE tokenizar los datos de la tarjeta en el navegador usando el SDK de MercadoPago.js (`@mercadopago/sdk-react`). Los datos sensibles de la tarjeta NUNCA deben pasar por el servidor de Food Store (PCI DSS SAQ-A).

#### Scenario: Tokenización exitosa
- **WHEN** el cliente completa el formulario de `CardPaymentForm` con datos de tarjeta válidos
- **THEN** el SDK de MercadoPago.js genera un `card_token` en el navegador
- **THEN** el componente llama a `onToken(card_token)` con el token generado

#### Scenario: Tokenización fallida
- **WHEN** el SDK de MercadoPago.js no puede generar un token (tarjeta inválida, expirada, etc.)
- **THEN** se muestra un mensaje de error específico de MP en el formulario
- **THEN** el cliente puede corregir los datos e intentar de nuevo

#### Scenario: MercadoPago.js no se inicializa
- **WHEN** la `VITE_MP_PUBLIC_KEY` no está configurada o el CDN de MP falla
- **THEN** se muestra un mensaje de error claro indicando que el sistema de pago no está disponible

---

### Requirement: Sistema crea pedido y luego procesa pago con MP
El sistema DEBE crear primero el pedido (`POST /pedidos/`) y luego, con el `pedido_id` obtenido, crear el pago en MercadoPago (`POST /pagos/crear`).

#### Scenario: Creación de pedido exitosa + pago exitoso
- **WHEN** el cliente hace clic en "Pagar"
- **THEN** se envía `POST /pedidos/` con los items del carrito, dirección y ubicación
- **THEN** al obtener `pedido_id`, se envía `POST /pagos/crear` con `pedido_id` y `card_token`
- **THEN** si ambas llamadas son exitosas, el sistema redirige a `/pedidos/{id}/confirmacion`
- **THEN** el carrito se limpia (clearCart)

#### Scenario: Creación de pedido fallida
- **WHEN** `POST /pedidos/` retorna error (ej: producto sin stock)
- **THEN** se muestra el mensaje de error del backend
- **THEN** el botón "Pagar" se vuelve a habilitar
- **THEN** NO se intenta crear el pago

#### Scenario: Pedido creado pero pago fallido
- **WHEN** `POST /pedidos/` es exitoso pero `POST /pagos/crear` falla (ej: tarjeta rechazada)
- **THEN** se muestra el error específico de MP
- **THEN** el cliente puede reintentar el pago con nuevos datos de tarjeta
- **THEN** el pedido permanece en estado PENDIENTE

#### Scenario: Doble clic en "Pagar"
- **WHEN** el cliente hace clic en "Pagar" mientras se procesa
- **THEN** el botón se deshabilita hasta que termine la operación
- **THEN** no se crean pedidos ni pagos duplicados

---

### Requirement: Cliente ve estado del pago en pantalla de confirmación
El sistema DEBE mostrar una pantalla de confirmación después del pago con el resultado del procesamiento.

#### Scenario: Pago aprobado
- **WHEN** el pago fue aprobado (`mp_status = "approved"`)
- **THEN** se muestra una pantalla verde con icono de éxito
- **THEN** se muestra el mensaje "¡Pago aprobado! Tu pedido está siendo procesado"
- **THEN** se muestra un botón "Ver detalle del pedido" que navega a `/pedidos/{id}`

#### Scenario: Pago rechazado
- **WHEN** el pago fue rechazado (`mp_status = "rejected"`)
- **THEN** se muestra una pantalla con icono de error
- **THEN** se muestra el mensaje de error específico (ej: "Tarjeta rechazada")
- **THEN** se muestra un botón "Reintentar pago" que redirige a `/pago?pedido_id={id}`

#### Scenario: Pago pendiente (en proceso)
- **WHEN** el pago fue creado pero el webhook de MP aún no respondió
- **THEN** se muestra una pantalla con icono de espera
- **THEN** se muestra el mensaje "Estamos procesando tu pago..."
- **THEN** la página hace polling cada 3s hasta obtener estado definitivo

#### Scenario: Timeout de polling
- **WHEN** pasaron 2 minutos sin obtener estado definitivo
- **THEN** se detiene el polling
- **THEN** se muestra "El pago está en proceso. Volvé más tarde."
- **THEN** se muestra un botón "Ver pedido" que navega a `/pedidos/{id}`

---

### Requirement: Sistema hace polling del estado de pago
El sistema DEBE consultar periódicamente `GET /pagos/{pedido_id}` para detectar cuándo el webhook de MercadoPago actualiza el estado.

#### Scenario: Polling encuentra pago aprobado
- **WHEN** el polling consulta `GET /pagos/{pedido_id}` y `mp_status = "approved"`
- **THEN** se detiene el polling
- **THEN** se muestra la pantalla de pago aprobado

#### Scenario: Polling encuentra pago rechazado
- **WHEN** el polling consulta `GET /pagos/{pedido_id}` y `mp_status = "rejected"`
- **THEN** se detiene el polling
- **THEN** se muestra la pantalla de pago rechazado

---

### Requirement: Cliente puede reintentar un pago rechazado
El sistema DEBE permitir al cliente reintentar el pago si el intento anterior fue rechazado, sin tener que volver al carrito.

#### Scenario: Reintento de pago
- **WHEN** el cliente hace clic en "Reintentar pago" desde la confirmación
- **THEN** el sistema redirige a `/pago?pedido_id={id}`
- **THEN** la PagoPage reconoce el `pedido_id` en la URL y permite pagar el pedido existente
- **THEN** al enviar, se llama a `POST /pagos/crear` con un nuevo `card_token` y el mismo `pedido_id`
- **THEN** el backend maneja la idempotencia y evita duplicados

---

### Requirement: Mock de pago sigue disponible para desarrollo
El sistema DEBE mantener el endpoint `POST /pagos/mock` y su flujo asociado como alternativa para desarrollo sin conexión a MercadoPago.

#### Scenario: Pago mock desde frontend
- **WHEN** el frontend tiene la variable `VITE_MP_PUBLIC_KEY` vacía o un flag de mock activo
- **THEN** el formulario de tarjeta simulado (mock) se muestra en lugar de CardPaymentForm
- **THEN** al pagar, se llama a `POST /pagos/mock` en lugar de `POST /pagos/crear`
