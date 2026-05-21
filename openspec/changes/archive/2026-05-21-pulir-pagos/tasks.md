## 1. Modelo — Pago

- [x] 1.1 Fix timezone en `Pago.created_at` y `Pago.updated_at`: `datetime.utcnow` → `datetime.now(timezone.utc)`
- [x] 1.2 No persisitir `card_token`: en `PagoService.crear_pago()` no asignar `card_token` al crear el Pago

## 2. Service — Cleanup

- [x] 2.1 Eliminar dead code: remover línea `PedidoRepository(uow.session)` en `PagoService.crear_pago()`
- [x] 2.2 Agregar `APP_URL` a Settings con fallback a `CORS_ORIGINS` actual
- [x] 2.3 Reemplazar `CORS_ORIGINS.split(',')[0].strip()` por `settings.app_url` en todas las ocurrencias de `PagoService.crear_pago()`
- [x] 2.4 Validar `external_reference` en `PagoService.procesar_webhook()`: try/except al parsear, no crear Pago si pedido_id es inválido

## 3. Tests

- [x] 3.1 Test timezone: verificar que `Pago.created_at` tiene tzinfo (no naive)
- [x] 3.2 Test card_token no persistido: crear pago con card_token y verificar que en BD es NULL
- [x] 3.3 Test external_reference inválida: webhook con formato inesperado no crea Pago huérfano
