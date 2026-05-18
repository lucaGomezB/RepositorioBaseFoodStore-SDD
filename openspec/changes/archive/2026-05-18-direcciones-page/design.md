## Context

The backend API for delivery addresses (`/api/v1/direcciones/`) is fully implemented with:
- `POST /` — Create (auto-marks first as default per RN-DI01)
- `GET /` — List own addresses (ownership filtered by JWT)
- `PUT /{id}` — Update (ownership validated)
- `DELETE /{id}` — Delete (ownership validated, returns 204)
- `PATCH /{id}/predeterminada` — Set as default (atomic unset previous)

The frontend already has:
- TanStack Query hooks in `entities/address/api.ts` (`useDirecciones`, `useCreateDireccion`, `useUpdateDireccion`, `useDeleteDireccion`, `useSetDefaultDireccion`)
- TypeScript types in `entities/address/index.ts`
- Sidebar entry at `/direcciones` for roles CLIENT(4) and ADMIN(1)

Missing: route in `router.tsx` and page component.

## Goals / Non-Goals

**Goals:**
- Create `DireccionesPage.tsx` with full CRUD UI for delivery addresses
- Register `/direcciones` route under CLIENT+ADMIN protection
- Follow the existing project's CRUD page pattern (useReducer + inline forms as seen in `IngredientesCRUD.tsx` and `CategoriasCRUD.tsx`)
- Show visual indicator for default address
- Handle loading, error, and empty states

**Non-Goals:**
- No backend changes (API is complete)
- No new TanStack Query hooks (already exist)
- No changes to checkout flow or address snapshot logic
- No changes to admin panels

## Decisions

1. **Pattern: useReducer over TanStack Query for page state**
   - The existing CRUD pages (`IngredientesCRUD`, `CategoriasCRUD`) use `useReducer` for local state and call API functions directly inside handlers.
   - Although TanStack Query hooks exist, mixing TanStack Query's declarative caching with imperative mutation handlers in the same page adds complexity without benefit for this simple CRUD.
   - Decision: Use the established `useReducer` + direct API call pattern for consistency with existing pages, using `httpClient` directly (not the legacy `apiFetch`).

2. **Form: Inline form (not modal)**
   - Consistent with existing CRUD pages in the project (`IngredientesCRUD.tsx` uses an inline expandable form).
   - Modals add complexity (portal, focus trap, overlay). The project doesn't use modals for CRUD forms.

3. **Default address: PATCH button with visual badge**
   - Use a prominent "Predeterminada" badge for the current default.
   - "Establecer como predeterminada" button on non-default addresses.
   - Matches RN-DI01, RN-DI02 from the docs.

## Risks / Trade-offs

- **Risk**: Deleting an address that is referenced by existing orders.
  → **Mitigation**: Backend uses soft-delete or validates no active orders. The frontend shows a confirmation dialog before deleting.
- **Trade-off**: Using `useReducer` instead of TanStack Query means we lose automatic cache invalidation on mutation. The page manually refetches after each operation, which is consistent with the existing pattern.
