## Why

Users cannot save or edit delivery addresses because: (1) the frontend httpClient never sends auth credentials or Bearer tokens, causing all authenticated API calls to return 401; (2) the Direccion model lacks coordinate fields (latitud/longitud), making it impossible to select or store a geographic location.

## What Changes

- Fix frontend httpClient: add `withCredentials: true`, wire Bearer token interceptor from authStore, integrate the existing `errorInterceptor.ts` for 401 refresh handling
- Add optional `latitud` (Float) and `longitud` (Float) fields to the Direccion model, schema, and service
- Fix the `actualizar` service method that filters out None values, preventing clearing of optional fields
- Add location selection UI on DireccionesPage using browser Geolocation API + manual coordinate input
- Update Direccion frontend types to include latitud/longitud

## Capabilities

### New Capabilities
None — all changes extend existing capabilities.

### Modified Capabilities
- `direcciones-crud`: Add latitud/longitud optional fields to create/update schemas and UI; add location selection via Geolocation API + manual input; fix actualizar service to allow clearing optional fields

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/models/direccion.py` | Modified | Add latitud (Float?), longitud (Float?) columns |
| `backend/app/domain/direcciones/schemas.py` | Modified | Add latitud/longitud to base schemas |
| `backend/app/domain/direcciones/service.py` | Modified | Fix `actualizar` None-filtering bug |
| `frontend/src/shared/api/httpClient.ts` | Modified | Add withCredentials, Bearer interceptor, wire error handling |
| `frontend/src/shared/api/errorInterceptor.ts` | Modified | Integrate as wired middleware (currently dead code) |
| `frontend/src/entities/address/` | Modified | Update types with lat/lng fields |
| `frontend/src/pages/DireccionesPage.tsx` | Modified | Add location selection UI |
| `backend/app/domain/direcciones/` | New | Migration for latitud/longitud columns |
