## Context

El frontend tiene `authStore` con `user.rol_id` y `isLoggedIn`. Existe router.tsx como placeholder. El App.tsx actual renderiza un header simple y un placeholder. No hay navegación entre secciones.

Los roles tienen IDs: ADMIN=1, STOCK=2, PEDIDOS=3, CLIENT=4.

## Goals / Non-Goals

**Goals:**
- Sidebar responsivo con items de navegación filtrados por rol
- Header con branding + menú de usuario (login/logout)
- Layout que envuelva las rutas con sidebar + main content
- Definición centralizada de items de menú por rol

**Non-Goals:**
- Route guards / protección de rutas (change `frontend-auth-guards`)
- Lazy loading de módulos
- Diseño mobile avanzado (responsive básico sí)

## Decisions

### 1. Sidebar vs Top Navbar
**Decisión**: Sidebar lateral izquierdo (collapsible en mobile).

**Razón**: El sidebar permite agrupar muchas opciones sin ocupar espacio vertical, y es el patrón estándar para dashboards/admin panels.

### 2. Definición de Menú Items
**Decisión**: Array de objetos con `label`, `path`, `icon`, `allowedRoles` (array de Role). Se filtran con `useAuthStore`.

**Razón**: Centralizado, fácil de mantener y extender. Cada nuevo módulo solo agrega un item.

### 3. React Router
**Decisión**: Usar `<Link>` y `<NavLink>` de react-router-dom para navegación SPA. El router se configura con las rutas existentes.

**Razón**: El proyecto ya tiene react-router-dom como dependencia.

## Risks / Trade-offs

- **Riesgo**: Sidebar visible en páginas públicas (login).
  → **Mitigación**: LoginPage tiene su propio layout sin sidebar. Se controla con una prop `showSidebar` en el layout.
