## Context

El CRUD de productos (products-catalog-crud) está archivado. Los modelos M2M `ProductoCategoria` y `ProductoIngrediente` ya existen con sus tablas pivote. Los endpoints individuales (GET lista, POST agregar 1, DELETE 1) ya están implementados en el router y service.

**Problemas identificados:**
1. Las user stories US-016/US-017 especifican endpoints `PUT` que reemplazan TODAS las relaciones de un producto de una sola vez (body: array de IDs). No existen.
2. `add_ingrediente()` y `add_categoria()` en el service acceden `data.ingrediente_id` y `data.categoria_id` como atributos de objeto, pero reciben un `dict` — crash en runtime.
3. Las tablas pivote no tienen unique constraints compuestas — permiten duplicados.

## Goals / Non-Goals

**Goals:**
- Endpoints `PUT /api/v1/productos/{id}/ingredientes` y `PUT /api/v1/productos/{id}/categorias` con reemplazo atómico
- Corregir bug de dict access en service
- Agregar unique constraints compuestas + migración
- Tests para todos los endpoints de relaciones

**Non-Goals:**
- Frontend de gestión de relaciones (se aborda cuando se actualicen las páginas de productos)
- Catálogo público con relaciones expandidas (change #19)

## Decisions

### 1. PUT como reemplazo atómico vs merge
**Decisión**: El endpoint PUT elimina todas las relaciones existentes e inserta las nuevas en una sola transacción (UnitOfWork).

**Razón**: Es la semántica estándar de PUT (reemplazar el recurso completo). La user story dice "PUT ... body: array de IDs". Usar UoW garantiza atomicidad: si algo falla, todo se revierte.

### 2. PUT convive con POST/DELETE individuales
**Decisión**: Mantener los endpoints POST (agregar 1) y DELETE (eliminar 1) existentes. El PUT es adicional para reemplazo masivo.

**Razón**: Hay casos de uso para ambos. POST/DELETE son más convenientes para operaciones individuales desde el frontend. PUT es útil para sincronización completa.

### 3. Unique constraints en BD
**Decisión**: Agregar unique constraints compuestas `(producto_id, categoria_id)` y `(producto_id, ingrediente_id)` vía migración Alembic.

**Razón**: Evita duplicados a nivel BD. Es más robusto que validar en aplicación (race conditions).

## Risks / Trade-offs

- **Riesgo**: PUT sin datos enviados (`[]`) eliminaría todas las relaciones.
  → **Mitigación**: Es comportamiento esperado — un producto sin categorías/ingredientes es válido.
- **Riesgo**: `ON DELETE CASCADE` en FKs puede borrar relaciones si se elimina un producto/categoría/ingrediente.
  → **Mitigación**: Es el comportamiento deseado — consistencia referencial.
- **Riesgo**: Agregar unique constraints a tablas con datos existentes podría fallar si ya hay duplicados.
  → **Mitigación**: En desarrollo no hay datos duplicados (BD vacía o seed controlado).
