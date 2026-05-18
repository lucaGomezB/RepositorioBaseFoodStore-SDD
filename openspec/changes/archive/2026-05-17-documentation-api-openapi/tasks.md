## 1. Normalizar tags OpenAPI

- [x] 1.1 Corregir tags en backend/app/api/catalogo.py (usar "Catalog" en vez de "Catalogo Publico")
- [x] 1.2 Dividir tag "Admin / Metrics" en sub-tags: "Admin / Dashboard", "Admin / Users", "Admin / Orders", "Admin / Stock", "Admin / Config"
- [x] 1.3 Agregar tags a endpoints root y health que actualmente no tienen

## 2. Completar response_model

- [x] 2.1 Identificar endpoints sin response_model (los que retornan dict)
- [x] 2.2 Agregar response_model a endpoints faltantes en admin.py
- [x] 2.3 Agregar response_model a endpoints faltantes en auth.py

## 3. Agregar ejemplos en schemas

- [x] 3.1 Agregar json_schema_extra con examples en schemas de auth (login request/response)
- [x] 3.2 Agregar examples en schemas de productos, categorias, ingredientes
- [x] 3.3 Agregar examples en schemas de pedidos y pagos

## 4. Verificar documentacion

- [x] 4.1 Verificar que GET /docs carga Swagger UI sin errores
- [x] 4.2 Verificar que GET /redoc carga ReDoc sin errores
- [x] 4.3 Verificar que cada endpoint tiene description en el decorador
- [x] 4.4 Verificar response_model del GET /admin/usuarios con pagination

## 5. Testing

- [x] 5.1 Ejecutar pytest (251 tests deben seguir pasando)
- [ ] 5.2 Verificar build frontend (npm run build) — Error preexistente en archivos de test frontend (vitest/no relacionados con cambios backend)
