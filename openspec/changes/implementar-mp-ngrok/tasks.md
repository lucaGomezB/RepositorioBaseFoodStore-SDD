## 1. Documentación y setup

- [x] 1.1 Agregar `APP_URL` a `backend/.env.example` con comentario explicativo sobre ngrok
- [x] 1.2 Crear `docs/NGROK_SETUP.md` con paso a paso: instalar ngrok, `ngrok http 8000`, copiar URL a `.env`, configurar webhook en MP
- [x] 1.3 Excluir `docs/NGROK_SETUP.md` del repo via `.gitignore`

## 2. Backend — Webhook robusto

- [x] 2.1 Agregar rate limiting a `POST /api/v1/pagos/webhook` con slowapi (10 requests/min por IP)
- [x] 2.2 Mover procesamiento del webhook a `BackgroundTasks`: responder 200 inmediato, ejecutar lógica pesada en background (cuidado: la sesión de BD del `Depends(get_db)` se cierra al terminar el request — crear una sesión nueva dentro del background task o usar `Session` propia)
- [x] 2.3 Agregar `logger.info()` en cada paso del webhook (recepción, validación firma, consulta MP API, transición estado, broadcast)

## 3. Tests

- [x] 3.1 Test rate limiting: enviar 11 requests al webhook y verificar que el 11° retorna 429
- [x] 3.2 Test logging: verificar que el logger captura los pasos del webhook (usando `caplog` de pytest)

## 4. Setup manual (no código)

- [ ] 4.1 Probar flujo real con ngrok + MP: pago con tarjeta de prueba → webhook → CONFIRMADO → KDS
- [ ] 4.2 Ajustar según lo que se descubra en la prueba
