## Why

El panel de administración ya tiene métricas, usuarios y stock, pero la página de Configuración sigue siendo un placeholder con "Próximamente". Los administradores necesitan poder ajustar parámetros operativos del sistema (horarios de atención, costo de envío, etc.) sin necesidad de tocar código.

## What Changes

- Crear modelo `Configuracion` en backend (tabla key-value)
- Crear migración Alembic con seed data de configuraciones por defecto
- Crear schemas Pydantic para configuración
- Crear servicio y repositorio de configuración
- Implementar endpoints `GET /api/v1/admin/configuracion` y `PUT /api/v1/admin/configuracion`
- Agregar router admin con las rutas de configuración (o extender el existente)
- Crear página `ConfiguracionPage` en frontend con formulario de settings
- Reemplazar el placeholder en el router por el componente real

## Capabilities

### New Capabilities
- `system-config`: Panel de configuración del sistema con parámetros operativos editables (horarios, costos, valores por defecto)

### Modified Capabilities
- (ninguna — es nueva funcionalidad)

## Impact

- **Backend**: Nuevo modelo `Configuracion`, migración, schemas, repositorio, servicio y endpoints GET/PUT en `admin/configuracion`
- **Frontend**: Nueva página `ConfiguracionPage`, reemplazar placeholder en router
- **Seed data**: Agregar configuraciones por defecto al script de seed
