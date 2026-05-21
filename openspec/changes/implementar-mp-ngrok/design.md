## Context

`pulir-pagos` dejó todo listo: `APP_URL` configurable, `back_urls` y `notification_url` usan `settings.app_url`, firma HMAC-SHA256 implementada. Lo que falta es conectar con la infraestructura real de MercadoPago.

## Goals / Non-Goals

**Goals:**
- Poder recibir notificaciones webhook reales de MP vía ngrok
- Rate limiting en el webhook (endpoint público)
- Responder 200 inmediato y procesar en background (lo que MP espera)
- Documentación clara para cualquier developer del equipo

**Non-Goals:**
- No cambiar la lógica de negocio del webhook (ya funciona)
- No tocar el endpoint mock
- No hacer deploy a producción (solo desarrollo local con ngrok)

## Decisions

### D-1: BackgroundTasks de FastAPI vs Celery/ARQ
**Decisión:** `BackgroundTasks` de FastAPI.

**Razón:** Es parte del framework, no agrega dependencias, y para un webhook single-instance es suficiente. Si en el futuro necesitamos persistencia de tareas o colas, migramos a ARQ+Redis.

### D-2: Rate limiting con slowapi (mismo patrón que login)
**Decisión:** Usar `@limiter` con `limit("10/minute")`.

**Razón:** Ya está configurado en el proyecto para login, consistente.

## Risks / Trade-offs

- **BackgroundTasks en proceso**: si el servidor se cae antes de procesar, se pierde la notificación. MP reintentará automáticamente. Aceptable para v1.
- **ngrok URL cambia en cada reinicio**: hay que actualizar `APP_URL` en `.env` y la URL en el dashboard de MP cada vez. ngrok permite dominio fijo con plan pago.
