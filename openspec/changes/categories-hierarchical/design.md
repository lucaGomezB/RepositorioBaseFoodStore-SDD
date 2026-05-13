## Context

El modelo `Categoria` ya existe con `id`, `nombre`, `descripcion`, `parent_id` (autoreferencial), `orden_display`. El `CategoriaRepository` existe con `get_by_name`, `get_children`, `get_root_categories`. No hay schemas, service, ni router.

Reglas de negocio a implementar:
- RN-CA01: Jerarquía de profundidad arbitraria mediante FK autoreferencial (ya implementado en modelo)
- RN-CA02: No permitir ciclos ni auto-referencia en parent_id
- RN-CA03: No permitir eliminar categoría con productos activos (se valida cuando exista products-catalog-crud)
- RN-CA09: Soft delete (marcar con deleted_at, nunca borrar físicamente)

## Goals / Non-Goals

**Goals:**
- Schemas: CategoriaCreate, CategoriaUpdate, CategoriaResponse, CategoriaTree (anidado)
- Service: validaciones de negocio, CRUD, árbol jerárquico
- Router: CRUD completo + GET público con árbol
- Tests: CRUD + jerarquía + soft delete + RBAC

**Non-Goals:**
- ProductoCategoria M2M (se aborda en products-associations)
- Frontend (se aborda en dashboard CRUD pages y frontend-catalog-ui)

## Decisions

### 1. Árbol jerárquico vía CTE Recursivo vs Python
**Decisión**: Armar el árbol en Python desde el service (obtener todas las categorías y anidar).

**Razón**: Para catálogos pequeños (< 1000 categorías), es más simple y evita SQL complejo. Se optimiza a CTE si el volumen crece.

### 2. Endpoint público vs protegido
**Decisión**: GET /categorias es público (catalogo). POST/PUT/DELETE requieren STOCK o ADMIN.

**Razón**: El catálogo público debe ser accesible sin autenticación. La gestión requiere rol.

### 3. Soft Delete con deleted_at
**Decisión**: Agregar campo `deleted_at` al modelo. GET público excluye borrados. GET admin puede incluir `incluir_eliminados`.

**Razón**: RN-CA09 lo exige. Consistente con el resto del sistema.

## Risks / Trade-offs

- **Riesgo**: CTE recursivo en Python puede ser lento para muchos niveles.
  → **Mitigación**: Se empieza con árbol en Python. Si hay problemas de performance, se migra a CTE en SQL.
- **Riesgo**: Soft delete sin purga eventual acumula registros.
  → **Mitigación**: Baja prioridad ahora, se puede agregar job de limpieza después.
