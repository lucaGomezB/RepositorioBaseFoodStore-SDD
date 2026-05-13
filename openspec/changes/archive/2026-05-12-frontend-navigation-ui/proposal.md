## Why

El frontend actual no tiene navegación ni sidebar. Solo muestra un header fijo con "Food Store" y un placeholder. Los usuarios no pueden navegar entre las distintas secciones (catálogo, carrito, pedidos, admin, etc.). Cada rol (CLIENT, STOCK, PEDIDOS, ADMIN) debe ver solo las opciones de menú que le corresponden, y los usuarios no autenticados deben ver las opciones públicas.

## What Changes

- Crear componente `Sidebar` con items de navegación dinámicos según el rol del usuario
- Refactorizar `App.tsx` para incluir layout con sidebar + main content area
- Agregar menú de usuario (logout) en el header
- Definir menú items por rol según RN-RB06, RN-RB07 y US-075
- NO incluye route guards ni protección de rutas (se aborda en `frontend-auth-guards`)
- NO incluye lazy loading de módulos (se aborda en `frontend-auth-guards`)

## Capabilities

### New Capabilities
- `role-based-navigation`: Sidebar con items filtrados por rol del usuario autenticado

### Modified Capabilities
- (ninguna — es capability nueva)

## Impact

- **Frontend**: Nuevo componente `Sidebar` en `frontend/src/shared/components/Sidebar.tsx`. Modificación de `App.tsx` para layout con sidebar. Nuevo `SidebarItem` type.
- **Dependencias**: Utiliza `authStore` existente para obtener el rol del usuario.
- **No afecta backend** — es puramente frontend.
