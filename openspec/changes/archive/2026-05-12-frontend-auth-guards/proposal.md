## Why

El frontend actual no tiene protección de rutas ni manejo automático de tokens expirados. Cualquier usuario puede navegar a cualquier ruta, incluso sin estar autenticado. Además, cuando el access_token expira (15 min), el usuario recibe un error 401 sin que el sistema intente renovarlo automáticamente. Sin esto, la experiencia de usuario se rompe cada 15 minutos.

## What Changes

- Crear `ProtectedRoute` component que redirige al login si no hay sesión, y muestra 403 si el rol es insuficiente
- Crear HTTP client con Axios + interceptor que adjunte JWT automáticamente
- Implementar refresh automático en 401 con cola de requests (request queue)
- Refactorizar `router.tsx` para usar `ProtectedRoute` en rutas que lo requieran
- Refactorizar `api/client.ts` para usar el nuevo HTTP client con interceptor JWT

## Capabilities

### New Capabilities
- `auth-guards`: Route protection component with role checking + HTTP interceptor for automatic token refresh

### Modified Capabilities
- (ninguna — es capability nueva)

## Impact

- **Frontend**: Nuevo `shared/components/ProtectedRoute.tsx`, nuevo `shared/api/httpClient.ts` con Axios + interceptors
- **Dependencias**: Axios (ya en package.json), react-router-dom (ya instalado)
- **No afecta backend**
