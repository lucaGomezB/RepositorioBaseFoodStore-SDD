## Why

El frontend no muestra mensajes de error al usuario cuando algo falla. Los errores HTTP (400, 403, 404, 429, 500) no tienen feedback visual, y si un componente explota en renderizado, toda la UI se cuelga sin que el usuario sepa qué pasó.

## What Changes

- Crear `ErrorBoundary` component para capturar errores de renderizado con UI amigable
- Crear `ToastContainer` component para mostrar notificaciones del uiStore
- Agregar error interceptor en `httpClient` que muestre toasts automáticos según código HTTP
- Integrar ambos componentes en `App.tsx` / `AppLayout.tsx`

## Capabilities

### New Capabilities
- `frontend-error-handling`: Error boundary global + toast notification system + HTTP error interceptor

### Modified Capabilities
- (ninguna — es capability nueva)

## Impact

- **Frontend**: 2 nuevos componentes, modificación del httpClient y AppLayout
- **Dependencias**: Usa uiStore existente (addToast ya implementado)
