## 1. Types y hooks

- [x] 1.1 Agregar `telefono?: string` al `User` type en `shared/types/api.ts`
- [x] 1.2 Crear `entities/user/api.ts` con hooks `usePerfil()`, `useUpdatePerfil()`, `useChangePassword()`
- [x] 1.3 Completar `entities/address/index.ts` con hooks `useDirecciones`, `useCreateDireccion`, `useUpdateDireccion`, `useDeleteDireccion`, `useSetDefaultDireccion`

## 2. Components

- [x] 2.1 Crear `features/profile/components/ProfileInfo.tsx` con formulario de nombre y teléfono
- [x] 2.2 Crear `features/profile/components/PasswordChangeForm.tsx` con campos de contraseña actual y nueva
- [x] 2.3 Crear `features/profile/components/AddressManager.tsx` con lista, formulario, default, delete

## 3. Page + router

- [x] 3.1 Crear `pages/ProfilePage.tsx` que orquesta ProfileInfo + PasswordChangeForm + AddressManager
- [x] 3.2 Agregar ruta `/perfil` protegida (CLIENT, ADMIN) en el router
