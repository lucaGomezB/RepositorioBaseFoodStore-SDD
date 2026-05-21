## Why

El módulo de pagos tiene deuda técnica acumulada: timezone inconsistente (naive vs aware datetimes), código muerto (PedidoRepository instanciado sin usar), CORS_ORIGINS mal usado como base URL (se repite 4+ veces), external_reference parseado sin validación, y card_token persistido innecesariamente. Esto no afecta funcionalidad pero dificulta el mantenimiento y la futura integración con MercadoPago real.

Este change limpia todo eso sin cambiar comportamiento externo.

## What Changes

- **Fix timezone en modelo Pago**: `datetime.utcnow` → `datetime.now(timezone.utc)` en `created_at` y `updated_at`
- **card_token ya no se persiste**: el campo se queda en BD (nullable) pero no se guarda
- **Eliminar dead code**: `PedidoRepository(uow.session)` línea 70
- **Extraer base URL**: refactor de `CORS_ORIGINS.split(',')[0].strip()` a propiedad reutilizable
- **Validar external_reference**: manejo de errores al parsear, evitar Pago huérfano

## Capabilities

### New Capabilities
Ninguna — solo refactor interno.

### Modified Capabilities
- `payment-processing`: Refactor interno del service y modelo Pago. No cambia contratos de API.

## Impact

- `backend/app/models/pago.py`: Fix timezone en defaults
- `backend/app/domain/pagos/service.py`: Eliminar dead code, refactor base URL, validar external_reference, no guardar card_token
- `backend/app/api/pagos.py`: Sin cambios (API externa no cambia)
- `backend/tests/api/test_pagos.py`: Tests de timezone, mock, external_reference
