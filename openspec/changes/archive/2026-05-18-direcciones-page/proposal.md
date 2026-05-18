## Why

The sidebar already has a "Mis Direcciones" link pointing to `/direcciones`, but the route and page component are missing. Users with CLIENT or ADMIN roles cannot manage their delivery addresses despite the backend API being fully implemented (CRUD + set default). This leaves a gap in the user experience — users cannot add, edit, or delete their delivery addresses, which is required for the checkout flow (address selection when creating an order).

## What Changes

- **New page**: `DireccionesPage.tsx` — full CRUD UI for managing delivery addresses
- **New route**: `/direcciones` added to the CLIENT+ADMIN protected route group in `router.tsx`
- No backend changes needed (API at `/api/v1/direcciones/` is already complete)
- Uses existing TanStack Query hooks from `entities/address/api.ts`

## Capabilities

### New Capabilities
- `direcciones-crud`: Frontend CRUD for delivery addresses — list, create, edit, delete, and set default address, restricted to the owning user (CLIENT/ADMIN roles)

### Modified Capabilities
<!-- None — no existing specs are changing -->

## Impact

- Frontend only: `frontend/src/pages/DireccionesPage.tsx` (new file)
- `frontend/src/app/router.tsx` (new route import + route entry)
- No backend, database, or API changes
- No breaking changes
