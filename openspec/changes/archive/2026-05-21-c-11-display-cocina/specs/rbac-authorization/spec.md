## MODIFIED Requirements

### Requirement: Role Enum Definition
The system SHALL define an `IntEnum` with the 5 stable role IDs matching seed data: ADMIN(1), STOCK(2), PEDIDOS(3), CLIENT(4), COCINA(5).

#### Scenario: Role enum values match seed
- **WHEN** the Role enum is accessed
- **THEN** ADMIN SHALL equal 1, STOCK SHALL equal 2, PEDIDOS SHALL equal 3, CLIENT SHALL equal 4, COCINA SHALL equal 5

## ADDED Requirements

### Requirement: Endpoints de cocina protegidos por rol
El endpoint GET /api/v1/cocina/pedidos SHALL requerir roles COCINA, PEDIDOS o ADMIN. El WebSocket WS /api/v1/cocina/ws SHALL validar JWT en el handshake y requerir los mismos roles.

#### Scenario: Cocinero accede al KDS
- **WHEN** un usuario con rol COCINA hace GET /api/v1/cocina/pedidos
- **THEN** el backend retorna HTTP 200 con los pedidos de cocina

#### Scenario: CLIENT no accede al KDS
- **WHEN** un usuario con rol CLIENT hace GET /api/v1/cocina/pedidos
- **THEN** el backend retorna HTTP 403

### Requirement: Rol COCINA puede avanzar estado en fase cocina
El endpoint PATCH /api/v1/pedidos/{id}/estado SHALL aceptar el rol COCINA además de ADMIN y PEDIDOS. Sin embargo, la validación de qué transiciones permite cada rol vive en el service del FSM.

#### Scenario: COCINA autorizado al endpoint
- **WHEN** un usuario COCINA hace PATCH /pedidos/{id}/estado
- **THEN** pasa el require_roles (no recibe 403 por rol)

### Requirement: Seed de rol COCINA
El seed de datos SHALL incluir el rol COCINA con id=5 y nombre 'COCINA'. También SHALL incluir un usuario de prueba cocina@foodstore.com con ese rol.

#### Scenario: Seed ejecutado correctamente
- **WHEN** se ejecuta el seed
- **THEN** existe el registro Rol(id=5, nombre='COCINA')
- **THEN** existe el usuario cocina@foodstore.com con rol COCINA

#### Scenario: Seed es idempotente
- **WHEN** se ejecuta el seed dos veces
- **THEN** no se crean registros duplicados (ON CONFLICT DO NOTHING)
