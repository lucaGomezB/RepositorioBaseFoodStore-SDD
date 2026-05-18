## Context

La API expone 45 endpoints via FastAPI. OpenAPI genera documentacion automatica desde los decoradores y type hints, pero hay problemas detectados:

- Tags con encoding incorrecto (Caracteres especiales en "Catalogo Publico")
- Endpoints sin tag agrupados en default
- Algunos endpoints sin response_model explicito
- Sin ejemplos en los schemas Pydantic
- Admin endpoints todos bajo un mismo tag "Admin / Metrics" en vez de sub-tags

## Goals / Non-Goals

**Goals:**
- Normalizar tags de OpenAPI: corregir encoding, agrupar en dominios logicos
- Agregar response_model a endpoints que actualmente retornan dict sin schema
- Agregar `json_schema_extra={"example": ...}` en schemas Pydantic clave
- Verificar que Swagger UI (/docs) y ReDoc (/redoc) sean funcionales
- Verificar que cada endpoint tenga status_code explicito y description

**Non-Goals:**
- No cambiar logica de negocio ni comportamiento de endpoints
- No agregar nuevos endpoints
- No modificar la especificacion OpenAPI manualmente (todo via decoradores FastAPI)
- No implementar autenticacion en /docs (se deja el default de FastAPI)

## Decisions

### 1. Correccion de tags via decoradores @router
**Decision**: Modificar los `tags` en cada router APIRouter para que usen nombres consistentes y sin caracteres especiales. Mantener el tag en ingles para consistencia con el codebase.

**Razon**: FastAPI usa los tags del APIRouter para agrupar endpoints en Swagger. Los caracteres no-ASCII causan problemas de encoding.

### 2. response_model en endpoints sin schema
**Decision**: Identificar endpoints que retornan `dict` sin `response_model` y agregar el schema correspondiente.

**Razon**: Sin response_model, Swagger no documenta la estructura de la respuesta.

### 3. Ejemplos via json_schema_extra
**Decision**: Usar `json_schema_extra={"example": ...}` en lugar de `Field(..., example=...)` que ya esta deprecado.

**Razon**: Consistente con el fix de Pydantic v2 aplicado en sesion anterior.

## Risks / Trade-offs

- **Riesgo**: Modificar tags puede romper clientes existentes que dependan del tag name.
  - **Mitigacion**: Los tags son puramente cosmeticos en Swagger, no afectan rutas.
- **Riesgo**: Agregar response_model puede exponer campos que antes estaban ocultos.
  - **Mitigacion**: Los schemas ya existen y son los mismos que usa la logica interna. No hay riesgo de seguridad adicional.
