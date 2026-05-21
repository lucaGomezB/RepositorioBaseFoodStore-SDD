## Context

El módulo `pagos/` fue implementado en changes anteriores (C-09 payments). Tiene varios issues de calidad que este change corrige. Todos son cambios internos — ningún endpoint cambia su contrato público.

## Goals / Non-Goals

**Goals:**
- Timezone consistente: todos los datetimes del proyecto usan `timezone.utc`
- Eliminar dead code
- No persistir datos sensibles innecesarios (card_token)
- Base URL no depende de CORS_ORIGINS
- external_reference parsing robusto

**Non-Goals:**
- No cambiar la API pública (requests/responses)
- No agregar funcionalidad nueva
- No tocar webhook flow real (se hará en implementar-mp-ngrok)

## Decisions

### D-1: card_token no se elimina de la BD
El campo se queda en la tabla `pagos` como nullable. No se hace migración ahora porque el change no incluye Alembic. Simplemente se deja de escribir el valor.

### D-2: base_url como property de Settings
Se agrega `APP_URL` a Settings. Si no está configurada, fallback al primer origen de `CORS_ORIGINS` (comportamiento actual). Esto permite que `implementar-mp-ngrok` solo configure `APP_URL` sin cambiar código.

## Risks / Trade-offs

- **card_token en BD**: Si alguien mira la BD, verá tokens viejos de antes de este change. Aceptable porque son tokens de un solo uso que expiran a las 24h.
- **APP_URL**: Si no se configura, el comportamiento es idéntico al actual. No hay breaking change.
