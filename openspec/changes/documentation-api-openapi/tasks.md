## 1. Normalizar tags OpenAPI

- [ ] 1.1 Corregir tags en backend/app/api/catalogo.py (usar "Catalog" en vez de "Catalogo Publico")
- [ ] 1.2 Dividir tag "Admin / Metrics" en sub-tags: "Admin / Dashboard", "Admin / Users", "Admin / Orders", "Admin / Stock", "Admin / Config"
- [ ] 1.3 Agregar tags a endpoints root y health que actualmente no tienen

## 2. Completar response_model

- [ ] 2.1 Identificar endpoints sin response_model (los que retornan dict)
- [ ] 2.2 Agregar response_model a endpoints faltantes en admin.py
- [ ] 2.3 Agregar response_model a endpoints faltantes en auth.py

## 3. Agregar ejemplos en schemas

- [ ] 3.1 Agregar json_schema_extra con examples en schemas de auth (login request/response)
- [ ] 3.2 Agregar examples en schemas de productos, categorias, ingredientes
- [ ] 3.3 Agregar examples en schemas de pedidos y pagos

## 4. Verificar documentacion

- [ ] 4.1 Verificar que GET /docs carga Swagger UI sin errores
- [ ] 4.2 Verificar que GET /redoc carga ReDoc sin errores
- [ ] 4.3 Verificar que cada endpoint tiene description en el decorador
- [ ] 4.4 Verificar response_model del GET /admin/usuarios con pagination

## 5. Testing

- [ ] 5.1 Ejecutar pytest (251 tests deben seguir pasando)
- [ ] 5.2 Verificar build frontend (npm run build)
