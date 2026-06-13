## 1. Backend — Model + Migration

- [ ] 1.1 Add `latitud: Optional[float] = Field(default=None)` and `longitud: Optional[float] = Field(default=None)` to `Direccion` model
- [ ] 1.2 Generate Alembic migration: `alembic revision --autogenerate -m "add_latitud_longitud_to_direcciones"`
- [ ] 1.3 Verify migration generates valid SQL (upgrade adds columns, downgrade removes them)

## 2. Backend — Schema Updates

- [ ] 2.1 Add `latitud: Optional[float] = None` and `longitud: Optional[float] = None` to `DireccionBase`
- [ ] 2.2 Add same optional fields to `DireccionUpdate`
- [ ] 2.3 Add Pydantic validators: latitud range [-90, 90], longitud range [-180, 180] (skip validation if None)

## 3. Backend — Service Fix

- [ ] 3.1 In `DireccionService.actualizar`, remove `if v is not None` filter: change `{k: v for k, v in data.items() if v is not None}` to `{k: v for k, v in data.items()}`
- [ ] 3.2 Verify that `actualizar` still ignores fields not sent by client (Pydantic schema already excludes them)
- [ ] 3.3 Verify that `actualizar` now allows clearing optional fields (piso_depto, latitud, longitud) by setting them to null

## 4. Frontend — httpClient Auth Wiring

- [ ] 4.1 Add `withCredentials: true` to axios.create config in `httpClient.ts`
- [ ] 4.2 Add request interceptor: read `accessToken` from authStore and set `Authorization: Bearer <token>` header
- [ ] 4.3 Add response error interceptor: on 401, attempt `POST /auth/refresh` with a refresh lock to prevent concurrent refreshes; on success, retry original request; on failure, redirect to `/login`
- [ ] 4.4 Wire `errorInterceptor.ts` via response interceptor success handler: call `handleHttpError` for non-401 errors

## 5. Frontend — Direccion Types

- [ ] 5.1 Add `latitud?: number` and `longitud?: number` to `Direccion` interface in `entities/address/index.ts`
- [ ] 5.2 Add `latitud?: number` and `longitud?: number` to `DireccionCreate` interface
- [ ] 5.3 Add `latitud?: number` and `longitud?: number` to `DireccionUpdate` interface

## 6. Frontend — DireccionesPage Location UI

- [ ] 6.1 Add latitud/longitud text inputs to the form in `DireccionesPage.tsx`, placed after codigo_postal
- [ ] 6.2 Add "Usar ubicación actual" button that calls `navigator.geolocation.getCurrentPosition()` and fills coordinate inputs
- [ ] 6.3 Add loading state while geolocation resolves; handle permission denied, timeout, and unavailable errors with inline messages
- [ ] 6.4 Add latitud/longitud columns to the address table display (format as "-34.6037, -58.3816")
- [ ] 6.5 Include latitud/longitud in create and update payloads sent to backend

## 7. Tests

- [ ] 7.1 Backend: test creating address with and without coordinates
- [ ] 7.2 Backend: test creating address with out-of-range lat/lng returns validation error
- [ ] 7.3 Backend: test `actualizar` clears optional fields when set to None
- [ ] 7.4 Backend: test migration upgrade and downgrade
- [ ] 7.5 Frontend: test httpClient request interceptor adds Bearer token when token exists in authStore
- [ ] 7.6 Frontend: test httpClient response interceptor calls refresh on 401 and retries
