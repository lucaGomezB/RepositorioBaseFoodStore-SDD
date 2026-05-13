## Context

El endpoint `GET /auth/me` existe pero está en el módulo de auth. Se creará un router separado `/api/v1/perfil` para mantener separación de concerns. Ya existen `bcrypt` (para verificar password) y `revoke_all_user_tokens()` (para forzar re-login).

## Goals / Non-Goals

**Goals:**
- GET /perfil: nombre, email, telefono, fecha_creacion
- PUT /perfil: editar nombre y teléfono
- PUT /perfil/password: cambiar password con verificación + revocar tokens
- Agregar telefono al modelo Usuario

**Non-Goals:**
- Frontend de perfil (change #23 frontend-profile-ui)
- Admin no puede ver/editar perfiles de otros (no está en las US)

## Decisions

### 1. Router separado de auth
**Decisión**: Crear `api/perfil.py` en vez de agregar a `api/auth.py`.

**Razón**: Separa concerns. Auth = login/tokens/registro. Perfil = datos personales/cambio password.

### 2. bcrypt.verify + revoke tokens en cambio de password
**Decisión**: Al cambiar password: verificar password actual con bcrypt.checkpw, hashear la nueva, persistir, llamar a `revoke_all_user_tokens()`.

**Razón**: US-063 lo exige. La función ya existe.

### 3. telefono nullable
**Decisión**: `telefono: Optional[str] = None` en el modelo.

**Razón**: Los usuarios existentes no tienen teléfono. No obligatorio al registrar.

## Risks / Trade-offs

- Revocar todos los tokens fuerza re-login en todos los dispositivos. Es intencional (seguridad).
