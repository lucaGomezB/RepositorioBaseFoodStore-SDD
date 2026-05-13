## Context

Backends listos: `GET/PUT /perfil`, `PUT /perfil/password`, CRUD `/direcciones`. Sidebar ya apunta a `/perfil`. authStore tiene `updateUser()`. Entities de address tienen types pero no hooks. User entity es stub.

## Goals / Non-Goals

**Goals:**
- ProfilePage con 3 secciones: info personal, cambio password, direcciones
- Hooks TanStack Query para perfil y direcciones
- Ruta `/perfil` protegida

**Non-Goals:**
- Catálogo, carrito, pedidos (otros changes)

## Decisions

### 1. Feature-sliced: features/profile/
**Decisión**: Componentes de perfil en `features/profile/`. ProfilePage es orchestrator.

**Razón**: Mismo patrón que features/catalog/. FSD consistente.

### 2. authStore.updateUser para refrescar perfil
**Decisión**: Después de editar perfil, llamar `authStore.getState().updateUser(data)`.

**Razón**: Ya existe. Evita inconsistentcias entre authStore y datos del perfil.

### 3. TanStack Query para direcciones
**Decisión**: Hooks en `entities/address/api.ts` con invalidación automática.

**Razón**: Consistente con entities/product/. No duplicar en Zustand.
