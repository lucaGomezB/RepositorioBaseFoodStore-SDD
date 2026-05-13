## Context

Food Store necesita integrar MercadoPago como pasarela de pagos para completar el ciclo de compra. Actualmente:

- Los pedidos se crean en estado PENDIENTE con snapshots de precio y dirección
- Existe el modelo `FormaPago` como catálogo (cargado via seed)
- Existe el `paymentStore.ts` en el frontend con estado para el flujo de checkout
- Las variables de entorno `MERCADOPAGO_ACCESS_TOKEN`, `MERCADOPAGO_PUBLIC_KEY` y `MERCADOPAGO_WEBHOOK_SECRET` ya están definidas en `config.py`
- NO existe modelo `Pago`, ni repositorio, ni servicio, ni endpoints de pago
- NO existe integración con el SDK de MercadoPago

Este diseño cubre exclusivamente el backend. La UI de checkout y el frontend de pagos se abordan en un cambio posterior.

## Goals / Non-Goals

**Goals:**
- Crear modelo `Pago` con todos los campos necesarios (mp_payment_id, mp_status, external_reference, idempotency_key)
- Implementar migración Alembic para la tabla `pagos`
- Crear schemas Pydantic: `PagoCreate`, `PagoRead`, `PagoWebhookRequest`
- Implementar `PagoRepository` con operaciones CRUD + búsqueda por pedido y external_reference
- Implementar `PagoService` con integración MercadoPago SDK (crear pago, verificar estado)
- Implementar `POST /api/v1/pagos/crear` — endpoint que recibe pedido_id y card_token, crea pago en MP y registra en BD
- Implementar `GET /api/v1/pagos/{pedido_id}` — consultar estado del pago de un pedido
- Implementar `POST /api/v1/pagos/webhook` — recibir notificaciones IPN de MP, actualizar estado del pago, y disparar transición de estado del pedido si corresponde
- Usar patrón Unit of Work para atomicidad transaccional

**Non-Goals:**
- UI de checkout / formulario de pago en frontend (cambio separado)
- Componente CardPayment con SDK MercadoPago.js (cambio separado)
- Polling de estado de pago desde frontend (cambio separado)
- Reintento de pago rechazado (US-048, se puede agregar después)
- Configuración del sistema (US-060, está en otro sprint)

## Decisions

### 1. Estructura del Modelo Pago

Se usan los mismos campos definidos en ERD v5 del Integrador.txt, adaptados al naming snake_case de SQLModel:

| Campo | Tipo | Restricción | Descripción |
|-------|------|-------------|-------------|
| id | BIGSERIAL | PK | ID interno |
| pedido_id | BIGINT | FK → pedidos.id, NN | Pedido asociado |
| mp_payment_id | BIGINT | UQ, NULL | ID devuelto por MercadoPago |
| mp_status | VARCHAR(30) | NN | pending/approved/rejected |
| external_reference | VARCHAR(100) | UQ, NN | UUID del Pedido como referencia MP |
| idempotency_key | VARCHAR(100) | UQ, NN | UUID generado por backend. Evita cobros duplicados |
| card_token | VARCHAR(255) | NULL | Token de tarjeta (solo para registro, no se persiste en producción) |
| status_detail | VARCHAR(255) | NULL | Detalle del estado devuelto por MP |
| created_at | TIMESTAMPTZ | NN, default NOW | Auditoría |
| updated_at | TIMESTAMPTZ | NN, auto-update | Auditoría |

### 2. Flujo de Creación de Pago

```
POST /api/v1/pagos/crear
Body: { pedido_id: int, card_token?: string, payment_method?: string }
```

1. Router valida body con `PagoCreateRequest`
2. Service abre UnitOfWork:
   - Verifica que el pedido existe y está en estado PENDIENTE
   - Genera `idempotency_key = uuid4()`
   - Verifica que no exista un pago con ese `idempotency_key` (idempotencia)
   - Prepara datos para MercadoPago: items del pedido, total, external_reference = pedido UUID
   - Llama a MercadoPago SDK para crear la orden/preferencia
   - Registra el resultado en tabla `Pago` con estado inicial
   - Si MP devuelve error, se registra igual pero con mp_status = "rejected"
   - Commit
3. Retorna PagoRead con datos del pago + preference URL

**Alternativa considerada**: Usar Orders API de MercadoPago (preferencia completa con items). Se descarta momentáneamente porque requiere configuración adicional de productos en MP. En su lugar se usa Payment API directa con card_token, que es más simple para una primera integración.

### 3. Flujo del Webhook IPN

```
POST /api/v1/pagos/webhook
Body: { type: "payment", data: { id: "mp_payment_id" } }
```

1. Router log ea la notificación y responde 200 inmediatamente (RN-PA03)
2. Service consulta la API de MercadoPago con el `mp_payment_id` para verificar el estado real (RN-PA04)
3. Abre UnitOfWork:
   - Busca `Pago` por `mp_payment_id`
   - Actualiza `mp_status` con el estado real de MP
   - Si `mp_status == "approved"`:
     - Usa `PedidoService.avanzar_estado()` para transicionar PENDIENTE → CONFIRMADO
     - El servicio de pedidos se encarga del decremento de stock (RN-FS03)
   - Si `mp_status == "rejected"`:
     - Solo actualiza el estado del pago, el pedido sigue PENDIENTE
   - Commit

**Validaciones de idempotencia**: El webhook verifica si ya se procesó una notificación con el mismo `mp_payment_id` y `mp_status` para evitar procesamiento duplicado.

### 4. Ubicación de Archivos

Siguiendo la estructura existente del proyecto:

```
backend/app/
├── api/
│   └── pagos.py              ← Router (endpoints)
├── core/
│   ├── repositories/
│   │   └── pago.py            ← PagoRepository
│   ├── services/
│   │   └── pago.py            ← PagoService
│   └── schemas/
│       └── pago.py            ← Schemas Pydantic
└── models/
    └── pago.py                ← Modelo SQLModel
```

### 5. SDK MercadoPago

Se utiliza el SDK oficial `mercadopago==2.3.0`. El SDK se inicializa como un singleton en el service de pago usando `MP_ACCESS_TOKEN` de la config:

```python
import mercadopago
sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
```

Los métodos principales del SDK:
- `sdk.payment().create(payment_data)` — para crear pagos con card_token
- `sdk.payment().get(mp_payment_id)` — para consultar estado de un pago

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| **Card token expirado**: El token de tarjeta de MP expira después de 7 días | El flujo de checkout es inmediato (el usuario no guarda el token), por lo que no debería expirar. Si ocurre, se retorna error para que el frontend solicite un nuevo token. |
| **Webhook duplicado**: MP puede enviar múltiples notificaciones para el mismo evento | Se usa `idempotency_key` + verificación de `mp_status` previo para evitar procesamiento duplicado. |
| **Falla de red al llamar a MP**: Timeout o error de conexión | Se implementa timeout de 10s en las llamadas HTTP al SDK. Si falla, se registra el error en BD y se retorna error 502 al cliente. |
| **Pedido no encontrado en webhook**: El pedido fue cancelado antes de que llegue la notificación | El service valida que el pedido esté en PENDIENTE antes de transicionar. Si no, solo actualiza el pago sin modificar el pedido. |
| **SDK de MP falla en modo test**: Las credenciales de prueba pueden tener limitaciones | Se documentan las tarjetas de prueba del sandbox en el README. Se configura un flag `MERCADOPAGO_SANDBOX=true` para facilitar debugging. |
| **Webhook público sin autenticación**: El endpoint /webhook es público por definición | Se valida la firma del webhook usando el header `X-Signature` de MP y el `MERCADOPAGO_WEBHOOK_SECRET`. Si no coincide, se retorna 403. |
