## Why

Los clientes necesitan ver y editar su perfil (nombre, teléfono) y cambiar su contraseña. Actualmente solo existe `GET /auth/me` que devuelve datos básicos. No hay endpoint para editar perfil ni cambiar password. Además, el modelo `Usuario` no tiene campo `telefono`.

## What Changes

- **Modelo**: Agregar `telefono` (string nullable) a `Usuario` + migración Alembic
- **Schemas**: PerfilResponse, PerfilUpdate, PasswordChange
- **Service**: PerfilService con ver perfil, editar perfil, cambiar password (con verificación bcrypt + revocar tokens)
- **Router**: 3 endpoints en `api/perfil.py` (GET, PUT perfil, PUT password)
- **Tests**: Tests para los 3 endpoints

## Capabilities

### New Capabilities
- `user-profile`: Visualización y edición de perfil de usuario, cambio de contraseña.

## Impact

- **Backend**: Nuevos: `backend/app/core/schemas/perfil.py`, `backend/app/core/services/perfil.py`, `backend/app/api/perfil.py`. Modificados: `backend/app/models/usuario.py`, `backend/alembic/versions/`, `backend/app/api/__init__.py`
- **Dependencias**: auth-login-register (JWT, bcrypt, tokens)
