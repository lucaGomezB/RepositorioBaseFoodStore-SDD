## 1. Setup y dependencias

- [x] 1.1 Agregar `mercadopago>=2.3.0` a `backend/requirements.txt`
- [x] 1.2 Verificar que las variables de entorno MP ya están en `config.py` (MERCADOPAGO_ACCESS_TOKEN, MERCADOPAGO_PUBLIC_KEY, MERCADOPAGO_WEBHOOK_SECRET)
- [x] 1.3 Agregar `.env.example` con los valores de MercadoPago documentados

## 2. Modelo Pago y migración

- [x] 2.1 Crear `backend/app/models/pago.py` con modelo SQLModel (tabla `pagos`)
- [x] 2.2 Importar Pago en `backend/app/models/__init__.py`
- [x] 2.3 Agregar relación `pagos` en el modelo Pedido
- [x] 2.4 Generar migración Alembic: `alembic revision --autogenerate -m "create_pagos_table"`
- [x] 2.5 Revisar y aplicar migración: `alembic upgrade head`

## 3. Schemas Pydantic para pagos

- [x] 3.1 Crear `backend/app/core/schemas/pago.py` con:
  - `PagoCreateRequest`: pedido_id, card_token (opcional), payment_method (opcional)
  - `PagoRead`: id, pedido_id, mp_payment_id, mp_status, external_reference, status_detail, created_at
  - `PagoWebhookRequest`: type (str), data (dict con id)
  - `PagoStatusResponse`: mp_status, status_detail, mp_payment_id, external_reference

## 4. Repositorio de pagos

- [x] 4.1 Crear `backend/app/core/repositories/pago.py` con `PagoRepository(BaseRepository[Pago])`:
  - `get_by_pedido_id`, `get_all_by_pedido_id`, `get_by_mp_payment_id`
  - `get_by_idempotency_key`, `get_by_external_reference`

## 5. Servicio de pagos (core)

- [x] 5.1 Crear `backend/app/core/services/pago.py` con `PagoService`:
  - SDK MP inicializado con `settings.MERCADOPAGO_ACCESS_TOKEN`
  - `crear_pago()`: valida pedido, genera idempotency_key, llama MP API, registra en BD
  - `obtener_pago_por_pedido()`: consulta con ownership check
  - `procesar_webhook()`: consulta MP API, actualiza estado, transiciona a CONFIRMADO si approved

## 6. Router de pagos

- [x] 6.1 Crear `backend/app/api/pagos.py` con:
  - `POST /pagos/crear` (CLIENT/ADMIN)
  - `GET /pagos/{pedido_id}` (auth + ownership check)
  - `POST /pagos/webhook` (público)
- [x] 6.2 Registrar router en `backend/app/api/__init__.py`

## 7. Tests de integración

- [x] 7.1 Escribir test de creación de pago exitoso (mockeando SDK de MP)
- [x] 7.2 Escribir test de creación de pago con pedido no encontrado (404)
- [x] 7.3 Escribir test de creación de pago con pedido no en PENDIENTE (409)
- [x] 7.4 Escribir test de idempotencia (múltiples pagos para mismo pedido)
- [x] 7.5 Escribir test de consulta de pago por pedido_id
- [x] 7.6 Escribir test de webhook con pago aprobado → transición a CONFIRMADO
- [x] 7.7 Escribir test de webhook con pago rechazado → pedido sigue PENDIENTE
- [x] 7.8 Escribir test de webhook duplicado (idempotencia)
- [x] 7.9 Escribir test de ownership: cliente no puede ver pago de otro usuario
