## Context

El sistema tiene 4 roles definidos en seed data con IDs estables: ADMIN(1), STOCK(2), PEDIDOS(3), CLIENT(4). El JWT contiene `rol_id` como claim. Existe una dependencia `require_admin()` en `app/core/auth/deps.py` que verifica `rol_id > 2`, pero no hay un mecanismo genérico para proteger endpoints con roles arbitrarios.

Actualmente ningún endpoint (excepto login/refresh) verifica permisos de forma consistente.

## Goals / Non-Goals

**Goals:**
- Crear `require_roles()` — dependency reutilizable que acepte lista de roles permitidos
- Refactorizar `require_admin()` para usar el nuevo mecanismo
- Agregar endpoint `PUT /api/auth/users/{id}/role` para asignación de roles por ADMIN
- Proteger rutas sensibles existentes (rate-limiting, error-handling, etc.)
- Implementar RN-RB04: impedir que último ADMIN se degrade
- Tests para cada combinación de rol/endpoint

**Non-Goals:**
- Múltiples roles por usuario (M2M) — se mantiene `rol_id` simple
- Frontend guards (se aborda en `frontend-auth-guards`)
- CRUD completo de usuarios (se aborda en `admin-users-management`)

## Decisions

### 1. Estrategia de Autorización
**Decisión**: Usar dependency injection de FastAPI con `Depends(require_roles(Role.ADMIN))` como decorador funcional.

**Alternativa considerada**: Middleware global con white/blacklist de rutas.
**Razón**: FastAPI dependencies son más explícitas, se ven en la documentación de OpenAPI, y permiten composición limpia (ej: `Depends(get_current_user), Depends(require_roles(Role.STOCK))`).

### 2. Enum de Roles vs Strings
**Decisión**: Usar `IntEnum` para roles con valores matching los IDs de seed data.

**Razón**: Type safety, autocompletado, y alineación con los IDs estables de la BD. Evita strings mágicas.

### 3. Endpoint de Asignación de Roles
**Decisión**: `PUT /api/auth/users/{user_id}/role` en el router de auth.

**Razón**: Por ahora solo ADMIN necesita asignar roles. Endpoint simple y testeable. Cuando llegue `admin-users-management` se puede migrar a un CRUD más completo.

### 4. Protección de Último ADMIN (RN-RB04)
**Decisión**: Verificar en el service que exista al menos otro ADMIN antes de permitir degradación.

**Razón**: Es una regla de negocio, no de infraestructura. Pertenece al service layer.

## Risks / Trade-offs

- **Riesgo**: El `rol_id` en el JWT queda desactualizado si un ADMIN cambia el rol del usuario.
  → **Mitigación**: El token JWT tiene expiración corta (15 min). El cambio de rol se refleja al refrescar el token. Para cambios críticos, se pueden invalidar refresh tokens del usuario.
- **Riesgo**: Dependencia rígida a IDs de roles numéricos.
  → **Mitigación**: El `Role` enum define los valores explícitamente. Si se agregan roles nuevos, se actualiza el enum.
