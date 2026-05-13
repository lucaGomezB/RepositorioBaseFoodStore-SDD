## Context

El modelo `Producto` ya existe con campos básicos: `id`, `nombre`, `descripcion`, `precio_base`, `imagenes_url`, `tiempo_prep_min`, `disponible`, `fecha_creacion`, `fecha_actualizacion`. El `ProductoRepository` existe con CRUD base. El `ProductoService` existe con operaciones CRUD. El router `backend/app/api/productos.py` expone endpoints CRUD.

**Gaps identificados vs. user stories:**
- Falta `stock_cantidad` (entero >= 0) — requerido por US-015 y US-021
- Falta `eliminado_en` (soft delete) — requerido por US-022, RN-CA09
- El delete actual no es soft delete real (solo actualiza fecha)
- Los endpoints requieren solo ADMIN, deben aceptar `[ADMIN, STOCK]`
- Falta endpoint `PATCH /stock` con actualización atómica (US-021)
- Falta filtros en GET list (categoría, búsqueda, disponibilidad)
- No existe frontend de gestión de productos

## Goals / Non-Goals

**Goals:**
- Agregar `stock_cantidad` y `eliminado_en` al modelo + migración Alembic
- Soft delete real en repository/service con filtro automático
- Endpoint `PATCH /api/v1/productos/{id}/stock` con UPDATE atómico
- Proteger endpoints con `require_roles(["ADMIN", "STOCK"])`
- Agregar filtros al GET list (categoria_id, busqueda, disponible)
- Frontend: entities/product/, CRUD pages para gestión, features/catalog/
- Schemas actualizados con stock_cantidad

**Non-Goals:**
- Catálogo público con paginación y filtros para clientes (change #19)
- Frontend de catálogo público (change #20)
- Refactor a módulos feature-first (`backend/modules/productos/`)
- Asociaciones M2M con categorías e ingredientes (change #18)

## Decisions

### 1. Stock en modelo Producto vs tabla separada
**Decisión**: Agregar `stock_cantidad` como columna directa en `Producto`.

**Razón**: Es un campo intrínseco del producto, 1:1. No justifica tabla separada. La US-021 requiere operación atómica, que se logra con `UPDATE productos SET stock_cantidad = stock_cantidad + delta WHERE id = :id AND stock_cantidad + delta >= 0`.

### 2. Soft delete en repository vs service
**Decisión**: Implementar `soft_delete()` en `ProductoRepository` con `UPDATE ... SET eliminado_en = NOW()`. Agregar filtro `WHERE eliminado_en IS NULL` en todas las queries de listado/obtención.

**Razón**: El `BaseRepository` genérico hace hard delete. Cambiarlo rompería otros módulos. Mejor implementar soft delete específico en ProductoRepository y agregar un flag `incluir_eliminados` para consultas admin.

### 3. Actualización atómica de stock
**Decisión**: Usar `UPDATE ... SET stock_cantidad = stock_cantidad + :delta WHERE id = :id AND (stock_cantidad + :delta) >= 0` dentro de una transacción.

**Razón**: Evita race conditions. Si dos requests llegan simultáneamente, cada UPDATE es atómico a nivel BD. La condición `>= 0` garantiza RN-CA05 sin necesidad de locks de aplicación.

### 4. Roles: require_roles(["ADMIN", "STOCK"])
**Decisión**: Usar el dependency `require_roles()` existente del módulo auth-rbac-roles con ambos roles.

**Razón**: Las user stories US-015 a US-022 especifican "Gestor de Stock" como actor. ADMIN también necesita acceso. El sistema ya tiene el Role.STOCK = 2 definido.

### 5. Frontend: TanStack Query + TanStack Form
**Decisión**: Usar TanStack Query para fetching/mutación de datos y TanStack Form para formularios.

**Razón**: Consistentes con las convenciones del proyecto AGENTS.md. No duplicar estado de servidor en Zustand.

## Risks / Trade-offs

- **Riesgo**: El modelo `Producto` actual usa `fecha_creacion`/`fecha_actualizacion` como strings, no datetime. Migrar a datetime rompe compatibilidad.
  → **Mitigación**: Mantener como strings por ahora. Los nuevos campos `stock_cantidad` (Integer) y `eliminado_en` (DateTime nullable) se agregan sin modificar los existentes.
- **Riesgo**: BaseRepository tiene `delete()` que hace hard delete. Si otro módulo lo usa, no podemos cambiarlo.
  → **Mitigación**: No tocar BaseRepository. ProductoRepository implementa su propio `soft_delete()` y `get_all()` con filtro.
- **Riesgo**: El código backend actual está en `backend/app/core/` y `backend/app/api/`, no en módulos feature-first como describe la arquitectura.
  → **Mitigación**: No refactorizar ahora. Trabajar sobre la estructura existente. El refactor se agenda como cambio separado.
