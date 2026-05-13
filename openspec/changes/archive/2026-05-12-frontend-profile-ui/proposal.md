## Why

Los backends de perfil de usuario (#22) y direcciones (#21) ya están archivados. Pero los clientes no tienen interfaz para ver/editar su perfil, cambiar contraseña o gestionar direcciones. La Sidebar ya tiene un link a `/perfil` que da 404.

## What Changes

- **User type**: Agregar `telefono`
- **entities/user/**: hooks TanStack Query para perfil
- **entities/address/**: hooks TanStack Query para direcciones
- **features/profile/**: ProfileInfo, PasswordChangeForm, AddressManager
- **pages/ProfilePage.tsx**: Página completa de perfil
- **router**: Ruta `/perfil` protegida

## Capabilities

### New Capabilities
- `frontend-profile-ui`: Interfaz de perfil de usuario con datos personales, cambio de contraseña y gestión de direcciones.

## Impact

- **Frontend**: `frontend/src/shared/types/api.ts`, `frontend/src/entities/user/api.ts`, `frontend/src/entities/address/api.ts`, `frontend/src/features/profile/`, `frontend/src/pages/ProfilePage.tsx`, `frontend/src/app/router.tsx`
