## 1. Modelo + migracion

- [x] 1.1 Agregar eliminado_en (DateTime nullable) a Usuario + migracion

## 2. Schemas

- [x] 2.1 Crear schemas: UsuarioRead, UsuarioUpdate, UsuarioRoleUpdate

## 3. Repository

- [x] 3.1 Agregar paginacion y busqueda a UsuarioRepository
- [x] 3.2 Implementar soft delete

## 4. Endpoints admin

- [x] 4.1 GET /admin/usuarios (paginado, busqueda nombre/email, filtro rol)
- [x] 4.2 PUT /admin/usuarios/{id} (editar datos)
- [x] 4.3 DELETE /admin/usuarios/{id} (soft delete)
- [x] 4.4 PUT /admin/usuarios/{id}/role (asignar rol, migrar desde auth.py)

## 5. Tests

- [x] 5.1 Test: listar usuarios paginado
- [x] 5.2 Test: buscar por nombre/email
- [x] 5.3 Test: editar usuario
- [x] 5.4 Test: soft delete usuario
- [x] 5.5 Test: asignar rol
- [x] 5.6 Test: no-admin no puede acceder
