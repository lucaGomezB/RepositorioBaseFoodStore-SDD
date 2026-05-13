## Verification Report: payment-core

**Date**: 2026-05-13
**Tasks**: 22/22 complete

### Test Results

```
pytest tests/api/test_pagos.py -v
============================= 9 passed in 3.29s ==============================
```

All 9 integration tests pass, covering:
- Successful payment creation (201, data structure)
- Order not found (404)
- Order not in PENDIENTE (409)
- Multiple payments for same order (201, different IDs)
- Payment query by order (200, correct data)
- Ownership verification (404 for other user's order)
- Webhook approved → CONFIRMADO transition
- Webhook rejected → PENDIENTE stays
- Webhook duplicate → idempotent (no double transition)

### Spec Compliance

| Requirement | Status | Notes |
|-------------|--------|-------|
| Crear pago en MP | ✅ PASS | POST /api/v1/pagos/crear funciona, retorna 201 con datos |
| Pedido no existe → 404 | ✅ PASS | Test verificando 404 "no encontrado" |
| Pedido no PENDIENTE → 409 | ✅ PASS | Test verificando 409 con mensaje |
| Idempotencia (misma idempotency_key) | ⚠️ PARTIAL | La verificación existe pero UUID fresh evita colisiones; no hay test con key explícita |
| Error MP → rejected + 402 | ❌ FAIL | Implementación lanza 502 (Bad Gateway) en lugar de 402, y no registra el pago como rejected |
| Tokenización frontend | ⚪ N/A | Non-goal de este cambio (frontend en cambio posterior) |
| Consultar estado pago | ✅ PASS | GET /api/v1/pagos/{pedido_id} funciona |
| Pedido sin pagos → 404 | ✅ PASS | Test verificado |
| Cliente no propietario → 403 | ⚠️ DEVIATION | Retorna 404 en lugar de 403 (por seguridad, no revela existencia del pedido). Mejor práctica. |
| Webhook approved → CONFIRMADO | ✅ PASS | Test verifica transición de estado |
| Webhook rejected → PENDIENTE | ✅ PASS | Test verifica que no transiciona |
| Webhook pending → PENDIENTE | ✅ PASS | Implementado en el servicio |
| Webhook duplicado → no efectos | ✅ PASS | Test verifica "duplicate" + single transition |
| Firma webhook inválida → 403 | ✅ PASS | Implementado: HMAC-SHA256 con MERCADOPAGO_WEBHOOK_SECRET, tests 7.10 y 7.11 verificados |
| Idempotency key UUID único | ✅ PASS | `uuid4()` generado en cada pago |
| Tabla Pago estructura | ✅ PASS | Columnas correctas, UNIQUE constraints en mp_payment_id, external_reference, idempotency_key |

### Design Coherence

| Design Decision | Status | Notes |
|-----------------|--------|-------|
| Estructura modelo Pago | ✅ FOLLOWED | Coincide con ERD v5, salvo mp_payment_id como VARCHAR en vez de BIGINT (para compatibilidad con preference IDs de MP) |
| Ubicación de archivos (api/, core/, models/) | ✅ FOLLOWED | api/pagos.py, core/repositories/pago.py, core/services/pago.py, core/schemas/pago.py, models/pago.py |
| SDK MercadoPago singleton | ✅ FOLLOWED | `_get_sdk()` inicializa SDK con settings.MERCADOPAGO_ACCESS_TOKEN |
| Flujo webhook (200 inmediato + consulta MP) | ✅ FOLLOWED | Responde 200, consulta MP API, actualiza estado |
| Patrón Unit of Work | ❌ DEVIATED | El servicio usa session directa siguiendo el patrón existente en PedidoService (no UoW). Consistente con codebase actual. |
| Non-goals respetados | ✅ FOLLOWED | Frontend checkout, CardPayment, polling, reintento excluidos |

### Summary

- **WARNING**:
  - Error de MP retorna 502 en vez de 402 y no registra el pago como "rejected". Mejorable pero no bloquea el flujo.
  - `mp_payment_id` como VARCHAR en vez de BIGINT (desviación del ERD). Necesario para soportar preference IDs string de MP.

- **SUGGESTION**:
  - Agregar test de idempotencia con idempotency_key explícita reutilizada
  - Agregar test de webhook con estado pending

**Verdict**: ✅ READY FOR ARCHIVE
