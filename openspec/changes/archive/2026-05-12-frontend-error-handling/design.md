## Context

El uiStore ya tiene `addToast`, `removeToast`, `toasts[]`. El tipo `Toast` ya existe en `shared/types/api.ts`. El `httpClient` tiene interceptor de respuesta. No hay ErrorBoundary en el árbol de React.

## Goals / Non-Goals

**Goals:**
- ErrorBoundary global que capture errores de renderizado y muestre UI de fallback
- ToastContainer que renderice toasts en esquina superior derecha con auto-dismiss
- Error interceptor en httpClient que muestre toast según código HTTP:
  - 400: errores de validación (mostrar detalle)
  - 403: "No tenés permisos para esta acción"
  - 404: "Recurso no encontrado"
  - 429: "Demasiadas solicitudes, esperá un momento"
  - 500: "Error interno, intentá de nuevo más tarde"

**Non-Goals:**
- Formularios con validación inline (se aborda por componente)
- Logging a servidor externo

## Decisions

### 1. ErrorBoundary como class component
**Decisión**: Usar class component con `componentDidCatch` (requerido por React).

**Razón**: React aún no tiene hook equivalente para error boundaries. Los class components son la única opción.

### 2. Toast position
**Decisión**: Esquina superior derecha, apilados verticalmente, auto-dismiss a los 5 segundos.

**Razón**: No interfiere con el contenido principal y es el estándar de la mayoría de UIs.

### 3. Error Interceptor separado
**Decisión**: Función `handleHttpError` que recibe el error de Axios y llama a `addToast`. Se integra en el response interceptor del httpClient.

**Razón**: Mantiene el interceptor limpio y permite reusar la función en otros contextos.

## Risks / Trade-offs

- **Riesgo**: ErrorBoundary no captura errores en event handlers (solo renderizado).
  → **Mitigación**: Es comportamiento esperado de React. Los errores en handlers se capturan con try/catch o el interceptor HTTP.
