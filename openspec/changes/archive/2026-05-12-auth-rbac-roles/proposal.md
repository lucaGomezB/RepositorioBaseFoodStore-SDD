## Why

El sistema ya tiene autenticación JWT (login, refresh, logout), pero no existe un mecanismo centralizado para proteger endpoints según el rol del usuario. Actualmente solo hay un `require_admin()` que chequea `rol_id > 2` — no escala a los 4 roles del sistema (ADMIN, STOCK, PEDIDOS, CLIENT). Sin RBAC formal, cualquier endpoint puede ser accedido por cualquier usuario autenticado, lo que es un riesgo de seguridad crítico.

## What Changes

- Crear un dependency `require_roles()` genérico que acepte lista de roles permitidos
- Refactorizar `require_admin()` existente para usar el nuevo mecanismo
- Agregar endpoint `PUT /api/auth/users/{id}/role` para que ADMIN asigne roles
- Agregar lógica de protección: último ADMIN no puede auto-degradarse (RN-RB04)
- Agregar tests unitarios para cada combinación de rol/ruta
- NO incluye M2M (múltiples roles por usuario) — se mantiene `rol_id` simple (se abordará en change futuro si es necesario)

## Capabilities

### New Capabilities
- `rbac-authorization`: Middleware/dependency de autorización por roles (403 si rol insuficiente, 401 sin token)

### Modified Capabilities
- (ninguna — es capability nueva)

## Impact

- **Backend**: Nuevo módulo `app/core/auth/authorization.py` con `require_roles()`. Modificación de `app/core/auth/deps.py` para refactorizar `require_admin()`.
- **API**: Nuevo endpoint `PUT /api/auth/users/{id}/role` (solo ADMIN)
- **Database**: No requiere cambios de esquema (se usa `rol_id` existente)
- **Tests**: Nuevo archivo `tests/api/test_rbac.py`
- **Frontend**: No afecta directamente (se aborda en change `frontend-auth-guards`)
