## Context

El panel admin ya tiene páginas de métricas, usuarios y stock. La ruta `/configuracion` existe pero es un placeholder. No hay modelo de datos ni endpoints para configuración del sistema.

## Goals / Non-Goals

**Goals:**
- Modelo `Configuracion` key-value en BD
- Seed data con valores por defecto (costo_envio, horarios)
- Endpoints GET/PUT /api/v1/admin/configuracion
- Página `ConfiguracionPage` con formulario editable

**Non-Goals:**
- Configuración por tenant/usuario (solo global)
- Cacheo de configuración (se lee de BD cada vez)

## Decisions

### 1. Modelo key-value

```python
class Configuracion(SQLModel, table=True):
    __tablename__ = "configuraciones"
    clave: str = Field(primary_key=True, max_length=100)
    valor: str = Field(max_length=500)
    descripcion: str | None
    updated_by: int | None  # FK a usuarios.id
    updated_at: datetime
```

Configuraciones iniciales (seed): `costo_envio`, `horario_apertura`, `horario_cierre`, `tiempo_estimado_entrega_min`, `telefono_contacto`, `direccion_local`.

### 2. API

- `GET /api/v1/admin/configuracion` → lista completa de configuraciones
- `PUT /api/v1/admin/configuracion` → actualización masiva (body: array de {clave, valor})

### 3. Frontend

Formulario simple con campos agrupados. Cada clave se mapea a un label descriptivo. Botón "Guardar" que hace PUT.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| Sin validación de tipos (todo string) | Validación en frontend + documentación del formato esperado |
| Sin auditoría histórica | Se registra `updated_by` y `updated_at` (último cambio) |
