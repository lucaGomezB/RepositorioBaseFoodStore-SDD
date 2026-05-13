## Why

Los clientes necesitan gestionar direcciones de entrega para poder recibir pedidos. Actualmente no existe modelo, API ni frontend de direcciones. Las US-024 a US-028 y las reglas RN-DI01 a RN-DI03 lo requieren.

## What Changes

- **Modelo `Direccion`**: Tabla `direcciones` con FK a `usuarios`, campos de dirección, `es_predeterminada`, y auditoría
- **Migración Alembic**: Crear tabla direcciones
- **Repository**: CRUD con filtro por usuario_id
- **Schemas**: DireccionCreate, DireccionUpdate, DireccionResponse
- **Service**: Lógica de negocio (auto-marcar 1ra como predeterminada, transacción cambio predeterminada, validación ownership)
- **Router**: 5 endpoints protegidos (POST, GET, PUT, DELETE, PATCH predeterminada)
- **Frontend entity**: Tipo + hooks TanStack Query

## Capabilities

### New Capabilities
- `addresses-delivery`: Gestión de direcciones de entrega para clientes.

## Impact

- **Backend**: Nuevos archivos: `backend/app/models/direccion.py`, `backend/app/core/schemas/direccion.py`, `backend/app/core/services/direccion.py`, `backend/app/core/repositories/direccion.py`, `backend/app/api/direcciones.py`. Modificados: `backend/app/models/__init__.py`, `backend/app/api/__init__.py`, `backend/app/core/dependencies.py`, `backend/alembic/versions/`
- **Frontend**: `frontend/src/entities/address/` (completar stub)
