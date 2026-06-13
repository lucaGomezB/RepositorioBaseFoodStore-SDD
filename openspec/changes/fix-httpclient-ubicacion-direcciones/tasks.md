## 1. Backend — Model + Migration

- [x] 1.1 Add `latitud: Optional[float] = Field(default=None)` and `longitud: Optional[float] = Field(default=None)` to `Direccion` model
- [x] 1.2 Generate Alembic migration: manually created `a4b5c6d7e8f9_add_latitud_longitud_to_direcciones.py` (no PostgreSQL available for autogenerate)
- [x] 1.3 Verify migration generates valid SQL (upgrade adds columns, downgrade removes them) — migration file verified

## 2. Backend — Schema Updates

- [x] 2.1 Add `latitud: Optional[float] = None` and `longitud: Optional[float] = None` to `DireccionBase`
- [x] 2.2 Add same optional fields to `DireccionUpdate`
- [x] 2.3 Add Pydantic validators: latitud range [-90, 90], longitud range [-180, 180] (skip validation if None)

## 3. Backend — Service Fix

- [x] 3.1 In `DireccionService.actualizar`, remove `if v is not None` filter: changed `{k: v for k, v in data.items() if v is not None}` to `{k: v for k, v in data.items()}`
- [x] 3.2 Verify that `actualizar` still ignores fields not sent by client — verified via test `test_actualizar_solo_coordenadas` (calle/numero/preserved without being sent)
- [x] 3.3 Verify that `actualizar` now allows clearing optional fields — verified via test `test_actualizar_limpia_campos_opcionales`

## 4. Frontend — httpClient Auth Wiring

- [x] 4.1 Add `withCredentials: true` to axios.create config in `httpClient.ts`
- [x] 4.2 Add request interceptor: read `accessToken` from authStore and set `Authorization: Bearer <token>` header
- [x] 4.3 Add response error interceptor: on 401, attempt `POST /auth/refresh` with a refresh lock to prevent concurrent refreshes; on success, retry original request; on failure, redirect to `/login`
- [x] 4.4 Wire `errorInterceptor.ts` via response interceptor success handler: call `handleHttpError` for non-401 errors
- [x] 4.5 Fix: guard clause to skip refresh flow for /auth/refresh, /auth/login, /auth/register (prevents recursive deadlock)

## 5. Frontend — Direccion Types

- [x] 5.1 Add `latitud?: number` and `longitud?: number` to `Direccion` interface in `entities/address/index.ts`
- [x] 5.2 Add `latitud?: number` and `longitud?: number` to `DireccionCreate` interface
- [x] 5.3 Add `latitud?: number` and `longitud?: number` to `DireccionUpdate` interface

## 6. Frontend — DireccionesPage Location UI

- [x] 6.1 Add latitud/longitud text inputs to the form in `DireccionesPage.tsx`, placed after codigo_postal
- [x] 6.2 Add "Usar ubicación actual" button that calls `navigator.geolocation.getCurrentPosition()` and fills coordinate inputs
- [x] 6.3 Add loading state while geolocation resolves; handle permission denied, timeout, and unavailable errors with inline messages
- [x] 6.4 Add latitud/longitud columns to the address table display (format as "-34.6037, -58.3816")
- [x] 6.5 Include latitud/longitud in create and update payloads sent to backend

## 7. Tests

- [x] 7.1 Backend: test creating address with and without coordinates — 6 test cases including boundary values
- [x] 7.2 Backend: test creating address with out-of-range lat/lng returns validation error — 6 test cases including boundaries
- [x] 7.3 Backend: test `actualizar` clears optional fields when set to None — test passes
- [ ] 7.4 Backend: test migration upgrade and downgrade — migration file created but not run (no DB available)
- [ ] 7.5 Frontend: test httpClient request interceptor adds Bearer token when token exists in authStore
- [ ] 7.6 Frontend: test httpClient response interceptor calls refresh on 401 and retries
