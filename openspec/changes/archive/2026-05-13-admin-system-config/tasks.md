## 1. Backend — Modelo y migración

- [x] 1.1 Crear `backend/app/models/configuracion.py` con modelo SQLModel (tabla `configuraciones`)
- [x] 1.2 Importar Configuracion en `backend/app/models/__init__.py`
- [x] 1.3 Generar migración Alembic y aplicar

## 2. Backend — Schemas, repositorio y servicio

- [x] 2.1 Crear `backend/app/core/schemas/configuracion.py` (ConfigRead, ConfigUpdateRequest)
- [x] 2.2 Crear `backend/app/core/repositories/configuracion.py` (get_all, upsert)
- [x] 2.3 Crear `backend/app/core/services/configuracion.py` (listar, actualizar)

## 3. Backend — Endpoints admin

- [x] 3.1 Agregar endpoints en `backend/app/api/admin.py`:
  - GET /admin/configuracion — listar configuraciones
  - PUT /admin/configuracion — actualizar configuraciones

## 4. Backend — Seed data

- [x] 4.1 Agregar configuraciones por defecto al script de seed (costo_envio, horarios, etc.)

## 5. Frontend — Página de configuración

- [x] 5.1 Crear `pages/ConfiguracionPage.tsx` con formulario de settings
- [x] 5.2 Reemplazar placeholder en `app/router.tsx` por ConfiguracionPage

## 6. Tests

- [x] 6.1 Test: GET /admin/configuracion retorna lista
- [x] 6.2 Test: PUT /admin/configuracion actualiza valores
- [x] 6.3 Test: PUT con clave inválida retorna 400
