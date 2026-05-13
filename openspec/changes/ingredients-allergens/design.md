## Context

Modelo `Ingrediente` existe sin `es_alergeno`. Repositorio `IngredienteRepository` existe con `get_by_name`. Mismo patrón arquitectónico que `categories-hierarchical`.

## Goals / Non-Goals

**Goals:**
- Agregar `es_alergeno: bool = False` al modelo
- Schemas: IngredienteCreate, IngredienteUpdate, IngredienteResponse
- Service: validación de nombre único
- Router: CRUD + GET público con filtro `?es_alergeno=true`
- Soft delete con `eliminado_en`
- Tests

**Non-Goals:**
- Asociación con productos (se aborda en products-associations)
- Frontend

## Decisions

### 1. Mismo patrón que categorías
**Decisión**: Misma estructura: schemas/ service/ router/ con `require_roles(STOCK, ADMIN)`.

**Razón**: Consistencia. El equipo ya conoce el patrón.

### 2. GET público con filtro opcional
**Decisión**: GET /ingredientes público. Query param `es_alergeno` opcional para filtrar.

**Razón**: US-012 requiere filtro por alérgeno. El catálogo público necesita ver ingredientes.
