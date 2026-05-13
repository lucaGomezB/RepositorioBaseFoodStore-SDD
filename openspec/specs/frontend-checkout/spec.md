## ADDED Requirements

### Requirement: Cliente puede ver pantalla de checkout con resumen del pedido
El sistema DEBE mostrar una pantalla de checkout después de crear un pedido, con el resumen de la compra y las opciones de pago disponibles.

#### Scenario: Ver checkout con pedido recién creado
- **WHEN** el cliente crea un pedido desde el carrito
- **THEN** el sistema redirige a `/checkout?pedido_id={id}`
- **THEN** la pantalla muestra: número de pedido, total, items con cantidades y precios, dirección de entrega snapshot, y el formulario de pago

---

### Requirement: Cliente puede pagar con tarjeta mediante MercadoPago
El sistema DEBE permitir al cliente ingresar los datos de su tarjeta en un formulario seguro proporcionado por MercadoPago.js, que tokeniza los datos sin enviarlos al servidor de Food Store (PCI DSS SAQ-A).

#### Scenario: Tokenización de tarjeta exitosa
- **WHEN** el cliente ingresa datos de tarjeta válidos en el `CardPaymentForm`
- **THEN** el SDK de MercadoPago.js genera un `card_token`
- **THEN** el botón "Pagar" se habilita
- **THEN** los datos de la tarjeta NUNCA se envían al backend

#### Scenario: Tokenización de tarjeta fallida
- **WHEN** el SDK de MercadoPago.js no puede generar un token (tarjeta inválida, expirada, etc.)
- **THEN** se muestra un mensaje de error claro sin recargar la página
- **THEN** el cliente puede corregir los datos e intentar de nuevo

#### Scenario: Pago procesado exitosamente
- **WHEN** el cliente hace clic en "Pagar" y el backend procesa el pago (POST /api/v1/pagos/crear)
- **THEN** el botón "Pagar" se deshabilita para evitar doble clic
- **THEN** se muestra un estado "Procesando pago..."
- **THEN** al recibir respuesta exitosa, se redirige a `/pedidos/{id}/confirmacion`

#### Scenario: Error al procesar pago
- **WHEN** el backend retorna un error al procesar el pago
- **THEN** se muestra el mensaje de error específico
- **THEN** el botón "Pagar" se vuelve a habilitar
- **THEN** el cliente puede intentar de nuevo

---

### Requirement: Cliente ve confirmación con estado del pago
El sistema DEBE mostrar una pantalla de confirmación después del pago, con el resultado del procesamiento.

#### Scenario: Pago aprobado
- **WHEN** el pago fue aprobado (`mp_status = "approved"`)
- **THEN** se muestra una pantalla verde con icono de éxito
- **THEN** se muestra el mensaje "¡Pago aprobado! Tu pedido está siendo procesado"
- **THEN** se muestra un botón "Ver detalle del pedido" que lleva a la página de detalle

#### Scenario: Pago rechazado
- **WHEN** el pago fue rechazado (`mp_status = "rejected"`)
- **THEN** se muestra una pantalla con icono de error
- **THEN** se muestra el mensaje de error específico (ej: "Tarjeta rechazada, intentá con otra")
- **THEN** se muestra un botón "Reintentar pago" que lleva de vuelta al checkout

#### Scenario: Pago pendiente (sin webhook aún)
- **WHEN** el pago fue creado pero el webhook de MP aún no respondió
- **THEN** se muestra una pantalla con icono de espera
- **THEN** se muestra el mensaje "Estamos procesando tu pago..."
- **THEN** el sistema hace polling cada 5 segundos hasta obtener el resultado o hasta 2 minutos

#### Scenario: Timeout de polling
- **WHEN** pasaron 2 minutos sin recibir confirmación del webhook
- **THEN** se muestra el mensaje "El pago está en proceso. Volvé más tarde para ver el estado."
- **THEN** se muestra un botón "Ver pedido" que lleva al detalle del pedido

---

### Requirement: Sistema hace polling del estado de pago
El sistema DEBE consultar periódicamente el estado del pago después de crearlo, para detectar cuándo el webhook de MercadoPago lo actualiza.

#### Scenario: Polling encuentra pago aprobado
- **WHEN** el polling consulta `GET /api/v1/pagos/{pedido_id}` y el estado es "approved"
- **THEN** se detiene el polling
- **THEN** se muestra la pantalla de pago aprobado

#### Scenario: Polling encuentra pago rechazado
- **WHEN** el polling consulta `GET /api/v1/pagos/{pedido_id}` y el estado es "rejected"
- **THEN** se detiene el polling
- **THEN** se muestra la pantalla de pago rechazado con opción de reintentar

---

### Requirement: Cliente puede reintentar un pago rechazado
El sistema DEBE permitir al cliente reintentar el pago si el intento anterior fue rechazado.

#### Scenario: Reintento de pago rechazado
- **WHEN** el cliente hace clic en "Reintentar pago" desde la pantalla de confirmación
- **THEN** el sistema redirige al checkout con el mismo `pedido_id`
- **THEN** el cliente puede ingresar nuevos datos de tarjeta
- **THEN** al enviar, se llama a `POST /api/v1/pagos/crear` con un nuevo `card_token`
- **THEN** el pedido permanece en estado PENDIENTE hasta que el nuevo pago sea procesado
