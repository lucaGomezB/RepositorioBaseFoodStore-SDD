## 1. Modelo

- [x] 1.1 Crear `backend/app/models/direccion.py` con modelo Direccion (SQLModel, table=True): FK usuarios, calle, numero, piso_depto, ciudad, codigo_postal, es_predeterminada, creado_en, actualizado_en
- [x] 1.2 Exportar Direccion en `backend/app/models/__init__.py`

## 2. Migración

- [x] 2.1 Crear migración Alembic para tabla direcciones

## 3. Schemas

- [x] 3.1 Crear `backend/app/core/schemas/direccion.py` con DireccionCreate, DireccionUpdate, DireccionResponse

## 4. Repository

- [x] 4.1 Crear `backend/app/core/repositories/direccion.py` con CRUD + filtrar por usuario_id

## 5. Service

- [x] 5.1 Crear `backend/app/core/services/direccion.py` con: crear (auto-marcar 1ra), listar_por_usuario, actualizar, eliminar, marcar_predeterminada (transacción atómica)

## 6. Router

- [x] 6.1 Crear `backend/app/api/direcciones.py` con 5 endpoints protegidos (CLIENT puede operar sus direcciones)
- [x] 6.2 Registrar router en `backend/app/api/__init__.py`
- [x] 6.3 Activar `get_direccion_repo()` en `backend/app/core/dependencies.py`

## 7. Tests

- [x] 7.1 Test: crear dirección como CLIENT
- [x] 7.2 Test: primera dirección se marca predeterminada
- [x] 7.3 Test: listar solo muestra direcciones del usuario
- [x] 7.4 Test: no se puede ver/editar/eliminar dirección de otro usuario (404)
- [x] 7.5 Test: marcar predeterminada desmarca la anterior
- [x] 7.6 Test: endpoints requieren autenticación

## 8. Frontend entity

- [x] 8.1 Completar `frontend/src/entities/address/index.ts` con tipo Direccion y hooks TanStack Query
