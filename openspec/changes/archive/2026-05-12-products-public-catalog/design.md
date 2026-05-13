## Context

El CRUD de productos está completo (products-catalog-crud) y las relaciones M2M también (products-associations). Los endpoints GET /productos y GET /productos/{id} existen y son públicos. Pero el catálogo público no cumple con los requisitos de las user stories:

- Falta filtro `excluir_alergenos` (US-023)
- Falta paginación con conteo total (US-018 pide `page`/`limit`)
- El detalle de producto no incluye ingredientes, alérgenos ni categorías (US-019)
- Se revela `stock_cantidad` exacta en vez de solo booleano (US-019)

## Goals / Non-Goals

**Goals:**
- Filtro `excluir_alergenos` en GET /productos (query con NOT EXISTS)
- Paginación con `page`/`limit` + `total_count` en respuesta
- GET /productos/{id} con ingredientes, categorías, stock como booleano
- Schema `ProductoCatalogoRead` separado del admin (no expone stock exacto, ni eliminado_en)
- Tests para comportamiento público

**Non-Goals:**
- Frontend de catálogo (change #20)
- Modificar endpoints administrativos (siguen igual)

## Decisions

### 1. Schema separado para catálogo público vs admin
**Decisión**: Crear `ProductoCatalogoRead` que excluye `stock_cantidad`, `eliminado_en`, e incluye `ingredientes: list[ProductoIngredienteRead]`, `categorias: list[ProductoCategoriaRead]` y `hay_stock: bool`.

**Razón**: El schema actual `ProductoRead` expone datos internos (stock exacto, eliminado_en). Separar evita exponer información sensible al cliente. Sigue el principio de "no exponer internal types" del python-design-patterns skill.

### 2. Filtro excluir_alergenos con NOT EXISTS
**Decisión**: Implementar como subquery `NOT EXISTS (SELECT 1 FROM producto_ingrediente WHERE ingrediente_id IN (:ids) AND producto_id = productos.id)`.

**Razón**: Es la forma más eficiente de excluir productos que contengan ciertos ingredientes. Una sola query, sin joins laterales.

### 3. Paginación: `page`/`limit` como alias
**Decisión**: Aceptar `page`/`limit` además de `skip`/`limit`. Internamente convertir: `skip = (page - 1) * limit`. Agregar header `X-Total-Count` o campo `total_count` en la respuesta.

**Razón**: La US-018 especifica `page`/`limit`. Mantener compatibilidad hacia atrás con `skip`/`limit` para no romper otros consumidores de la API.

### 4. Default disponible=true para anónimos
**Decisión**: En el endpoint GET público, si el usuario no está autenticado y no envía `disponible`, default a `true`. Usuarios autenticados pueden ver no disponibles si lo especifican.

**Razón**: RN-CA08 dice que el catálogo público solo muestra productos disponibles y no eliminados. El filtro de eliminados ya se maneja en el repository (eliminado_en IS NULL).

## Risks / Trade-offs

- **Riesgo**: El schema `ProductoCatalogoRead` duplica campos con `ProductoRead`.
  → **Mitigación**: Usar herencia de Pydantic o composición. Aceptable porque son contextos diferentes (admin vs público).
- **Riesgo**: La subquery NOT EXISTS puede ser lenta para muchos productos e ingredientes.
  → **Mitigación**: Los índices de FK ya existen. Si hay problemas de performance, se puede optimizar después.
