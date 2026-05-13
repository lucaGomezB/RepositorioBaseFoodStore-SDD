## Context

El frontend tiene `authStore` con `token` y `refreshToken`. El router usa react-router-dom v6 con rutas definidas. No hay protección de rutas ni manejo de 401. El HTTP client actual (`api/client.ts`) usa `fetch` nativo sin JNI.

US-076 requiere: redirigir al login si no auth, 403 si rol insuficiente, rutas públicas accesibles.
US-066 requiere: interceptor 401 → refresh automático → cola de requests → reintento.

## Goals / Non-Goals

**Goals:**
- `ProtectedRoute` component que acepte `requiredRoles` opcional
- HTTP client con Axios + interceptor que inyecte `Authorization: Bearer <token>`
- Refresh automático en 401: si expiró, llama a `/auth/refresh`, actualiza store, reintenta
- Request queue: si múltiples requests fallan simultáneamente por 401, solo una hace refresh
- Refactorizar router para usar `ProtectedRoute`

**Non-Goals:**
- Login/register forms (ya existen)
- Logout endpoint call (ya existe en backend)
- Refresh token desde componente (se maneja en interceptor)

## Decisions

### 1. Axios vs fetch con interceptor manual
**Decisión**: Usar Axios con interceptores.

**Razón**: Axios tiene interceptores nativos para request/response, manejo de colas más limpio, y mejor soporte para reintentos. El proyecto ya tiene Axios en package.json.

### 2. Refresh Queue Estrategia
**Decisión**: Variable `isRefreshing` + cola de promesas pendientes. Mientras se refresca, las requests entrantes se encolan. Al completar el refresh, se resuelven todas con el nuevo token.

**Razón**: Evita múltiples llamadas simultáneas a `/auth/refresh` cuando varias requests expiran a la vez.

### 3. ProtectedRoute Implementation
**Decisión**: Componente wrapper que usa `useAuthStore` para verificar auth + rol. Renderiza `<Outlet />` si autorizado, `<Navigate to="/login" />` si no auth, o un mensaje 403 si rol insuficiente.

**Razón**: Patrón estándar en React Router v6 para layouts protegidos.

## Risks / Trade-offs

- **Riesgo**: El interceptor de Axios necesita importar el store, lo que puede crear dependencias circulares.
  → **Mitigación**: El store es Zustand, no React Context. Se puede importar directamente sin ciclo.
- **Riesgo**: Múltiples pestañas abiertas pueden tener tokens desincronizados.
  → **Mitigación**: El store persiste en localStorage con `zustand/middleware/persist`. El interceptor lee del store siempre actualizado.
