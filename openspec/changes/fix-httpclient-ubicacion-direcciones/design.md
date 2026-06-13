## Context

The Direcciones CRUD is completely broken in production: every API call returns 401 because the frontend httpClient never sends auth credentials (no `withCredentials`, no Bearer token interceptor). Additionally, users cannot select a delivery location because the Direccion model has no coordinate fields and the UI has no location selector. The errorInterceptor.ts exists but is dead code — never wired to httpClient. The service layer also has a bug where `actualizar` filters out None values, preventing users from clearing optional fields.

## Goals / Non-Goals

**Goals:**
- Fix frontend httpClient auth: add `withCredentials: true`, wire Bearer token request interceptor, wire 401 refresh response interceptor, integrate errorInterceptor.ts for non-401 error toasts
- Add optional `latitud` and `longitud` fields to Direccion backend model, schemas, and migration
- Fix `actualizar` service method to accept explicit None values for clearing optional fields
- Add location selection UI on DireccionesPage using browser Geolocation API + manual coordinate inputs
- Add lat/lng columns to address list display

**Non-Goals:**
- No interactive map widget (Leaflet, Google Maps) — deferred to future change
- No backend geocoding (reverse/forward) — coordinates are user-provided only
- No changes to PagoPage geolocation flow
- No backend auth architecture changes — only frontend httpClient wiring

## Decisions

### D-1: Frontend httpClient Auth Wiring

**Approach:** Three simultaneous fixes in httpClient.ts.

1. **withCredentials: true** — add to axios.create config. This is essential for httpOnly refresh cookies to be sent cross-origin when the frontend and backend are on different ports/domains.

2. **Request interceptor** — before every request, read `accessToken` from `authStore` (Zustand). If present, set `Authorization: Bearer <token>`. This covers the case where the backend validates Bearer tokens (current design).

3. **Response interceptor (401)** — on 401 response, attempt `POST /auth/refresh` to rotate tokens. If refresh succeeds, retry the original request with the new token. If refresh fails, redirect to `/login` and clear authStore. This is a standard axios interceptor pattern with a "isRefreshing" lock to prevent concurrent refresh loops.

4. **Wire errorInterceptor.ts** — use `httpClient.interceptors.response.use()` to call `handleHttpError` for all non-401 errors. This gives users toast notifications for validation errors, 403s, 500s, etc.

**Alternatives considered:** Adding interceptors only for 401 (without Bearer) was considered but rejected because the backend code validates Bearer tokens directly, not just cookies. Both mechanisms are needed.

### D-2: Backend Model Migration

**Approach:** Add two optional Float columns to the existing `direcciones` table.

```python
# In Direccion model
latitud: Optional[float] = Field(default=None)
longitud: Optional[float] = Field(default=None)
```

Alembic auto-generation via `alembic revision --autogenerate -m "add_latitud_longitud_to_direcciones"`.

**Decision:** Use `Float` (not `Numeric`) — sufficient precision for delivery coordinates (±1 meter at ~6 decimal places). Optional fields to not break existing addresses.

### D-3: Backend Schema Updates

Add to `DireccionBase`:
```python
latitud: Optional[float] = None
longitud: Optional[float] = None
```

`DireccionResponse` inherits these automatically. `DireccionUpdate` gets the same fields as optional. This ensures lat/lng can be set on create and modify on update.

**Decision:** Fields in base schema so response always includes them (even as null for legacy addresses).

### D-4: Fix `actualizar` Service Method

**Problem:** Line 54 filters out None values: `{k: v for k, v in data.items() if v is not None}`. This prevents clearing `piso_depto` or the new lat/lng fields because explicit None values are dropped.

**Fix:** Remove the None filter. Change to `{k: v for k, v in data.items()}`. The Pydantic schema already excludes fields not sent by the client, so only explicitly provided fields appear in `data`. A value of `None` means "set this field to null" — which is valid.

**Risk:** Existing clients that never send certain fields won't have them in data, so those fields won't be touched. This is correct behavior and unchanged from the original design.

### D-5: Frontend Location Selection UI

**Approach:** No map API dependency. Two mechanisms:

1. **Geolocation API button:** "Usar ubicación actual" calls `navigator.geolocation.getCurrentPosition()` and fills lat/lng inputs. Shows a loading state while the browser resolves position. Handles errors (denied, unavailable, timeout) with inline message.

2. **Manual coordinate inputs:** Two plain text inputs (latitud, longitud) accepting decimal degrees with validation (`lat: -90 to 90, lng: -180 to 180`). Optional fields.

**UI placement:** Two additional fields in the address form grid, below codigo_postal. Also show lat/lng in the address table as a new column (abbreviated, e.g., "-34.6037, -58.3816").

**Decision:** No map dependency keeps this change scoped and avoids adding third-party libraries. A map picker can be added in a future change if needed.

## Risks / Trade-offs

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Geolocation API denied by user | Medium | Fall back to manual input; no blocking behavior |
| Request interceptor conflicts with existing cookie auth | Low | Interceptor only sets Bearer if token exists; cookies still sent via withCredentials |
| Concurrent 401s trigger multiple refresh calls | Medium | Use a promise-based lock: queue subsequent 401s until refresh completes, then retry all with new token |
| Backend rejects null lat/lng as invalid | Low | Validate: null is valid (optional), non-null must be within range (-90 to 90, -180 to 180) |
