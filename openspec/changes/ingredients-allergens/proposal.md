## Why

El sistema necesita gestionar ingredientes con su flag de alérgeno para asociarlos a productos e informar a los clientes sobre alérgenos. Actualmente existe el modelo `Ingrediente` y el repositorio, pero no tiene el campo `es_alergeno`, ni endpoints CRUD, ni service layer.

## What Changes

- Agregar campo `es_alergeno` al modelo Ingrediente
- Crear schemas Pydantic para request/response
- Crear service layer con validaciones (nombre único)
- Crear router CRUD: GET público, POST/PUT/DELETE solo STOCK y ADMIN
- Agregar tests de integración

## Capabilities

### New Capabilities
- `ingredient-management`: CRUD completo de ingredientes con flag de alérgeno

### Modified Capabilities
- (ninguna)

## Impact

- **Backend**: Modificar modelo Ingrediente (+es_alergeno). Nuevos archivos schemas, service, router, tests.
- **API**: GET /ingredientes (público con filtro opcional), POST/PUT/DELETE (STOCK/ADMIN)
