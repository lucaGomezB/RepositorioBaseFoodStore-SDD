# Proposal: setup-zustand-stores

## Why

Frontend needs global state management. Zustand is already installed but no stores exist. We need to establish the state architecture before building features that depend on it (auth, cart, UI components).

## What Changes

1. **authStore.ts** — Hybrid store (state + React Query for API logic)
2. **cartStore.ts** — Smart store with validation logic, math, and persist middleware
3. **uiStore.ts** — State-only store with simple setters/toggles

## Capabilities

### New Capabilities

- **auth-store**: User authentication state with JWT token management
- **cart-store**: Shopping cart with stock validation, price calculation, localStorage persistence
- **ui-store**: UI state (theme, sidebar, modals, notifications)

### Modified Capabilities

- (none) — New stores, no existing specs to modify

## Impact

- **Files created**: `frontend/src/shared/stores/`
- **Depends on**: setup-frontend-config (ya completado), add-jwt-auth (ya completado)
- **Breaking changes**: None — adds new functionality only