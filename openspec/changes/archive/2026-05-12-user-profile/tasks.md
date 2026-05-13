## 1. Modelo + migración

- [x] 1.1 Agregar campo `telefono: Optional[str] = None` al modelo Usuario
- [x] 1.2 Crear migración Alembic para agregar columna telefono

## 2. Schemas

- [x] 2.1 Crear `backend/app/core/schemas/perfil.py` con PerfilResponse, PerfilUpdate, PasswordChange

## 3. Service

- [x] 3.1 Crear `backend/app/core/services/perfil.py` con: get_profile, update_profile, change_password (bcrypt + revoke tokens)

## 4. Router

- [x] 4.1 Crear `backend/app/api/perfil.py` con GET /perfil, PUT /perfil, PUT /perfil/password
- [x] 4.2 Registrar router en `backend/app/api/__init__.py`

## 5. Tests

- [x] 5.1 Test: ver perfil
- [x] 5.2 Test: editar perfil (nombre, telefono)
- [x] 5.3 Test: cambiar password correctamente
- [x] 5.4 Test: cambiar password con contraseña actual incorrecta → 400
- [x] 5.5 Test: cambiar password con nueva débil → 422
- [x] 5.6 Test: endpoints requieren auth
