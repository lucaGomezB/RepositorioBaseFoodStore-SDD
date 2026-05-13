## Context

No existe nada de direcciones. Es greenfield. El patrón a seguir es el mismo que categorías, ingredientes, productos: model → schemas → repository → service → router.

`dependencies.py` ya espera `Direccion` en `app.models.direccion` y tiene `get_direccion_repo()` preparado.

## Goals / Non-Goals

**Goals:**
- Modelo Direccion con FK a usuario y auditoría
- CRUD completo con 5 endpoints
- Lógica de predeterminada con transacción atómica
- Validación de ownership por JWT userId

**Non-Goals:**
- Frontend de gestión de direcciones (se hará en frontend-profile-ui, change #23)
- Verificar pedidos activos al eliminar (depende de orders-creation-fsm, change #26 — se habilita después)

## Decisions

### 1. Estructura en app/models/ + app/core/ + app/api/
**Decisión**: Seguir el patrón existente de producto, categoría, ingrediente.

**Razón**: `dependencies.py` ya espera `app.models.direccion.Direccion`. Es consistente con el resto del backend actual.

### 2. Auto-marcar predeterminada en service
**Decisión**: En `crear()`, si el usuario no tiene direcciones, marcar como predeterminada automáticamente.

**Razón**: RN-DI01 lo exige.

### 3. Transacción al cambiar predeterminada
**Decisión**: En `marcar_predeterminada()`, quitar flag de la actual y setear en la nueva dentro de una transacción.

**Razón**: RN-DI02 requiere solo una predeterminada. La transacción evita estados inconsistentes.

## Risks / Trade-offs

- **Verificación de pedidos activos**: La US-027 pide validar que una dirección no tenga pedidos activos antes de eliminar. Como orders-creation-fsm no existe aún, esta validación se posterga.
- **Ownership**: Todas las operaciones filtran por `usuario_id` del JWT. RN-RB05 lo exige.
