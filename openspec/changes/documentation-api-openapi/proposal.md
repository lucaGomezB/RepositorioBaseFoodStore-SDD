## Why

La API tiene 45 endpoints pero la documentacion OpenAPI/Swagger tiene inconsistencias: tags mal codificados, endpoints sin tag, descripciones incompletas y el schema OpenAPI no esta optimizado para consumo por generadores de clientes. Esto dificulta el consumo de la API por parte de integradores externos y la depuracion durante desarrollo.

## What Changes

- Normalizar tags de OpenAPI: corregir encoding, agrupar endpoints administrativos en sub-tags logicos
- Agregar response_model a endpoints que falten
- Agregar descriptions detalladas a todos los endpoints (incluyendo codigos de error posibles)
- Verificar que /docs y /redoc sean accesibles y esten completos
- Agregar ejemplos de request/response en los schemas donde falten
- Verificar que todos los endpoints tengan status_code explicito

## Capabilities

### New Capabilities
- `api-documentation`: Estandarizacion y validacion de la documentacion OpenAPI/Swagger/ReDoc

### Modified Capabilities
Ninguna. No cambian requerimientos funcionales, solo documentacion.

## Impact

- `backend/app/api/*.py`: endpoint descriptions, status_code, response_model
- `backend/app/core/schemas/*.py`: ejemplos en schemas
- Accesible via /docs (Swagger UI) y /redoc (ReDoc)
- Sin cambios en logica de negocio
