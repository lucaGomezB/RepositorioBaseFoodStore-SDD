## 1. HTTP Client with JWT Interceptor

- [x] 1.1 Create `shared/api/httpClient.ts` with Axios instance
- [x] 1.2 Add request interceptor to attach JWT from authStore
- [x] 1.3 Add response interceptor for 401 handling with auto-refresh + request queue
- [x] 1.4 Export httpClient and helper hooks from `shared/api/`

## 2. Route Guard Component

- [x] 2.1 Create `shared/components/ProtectedRoute.tsx` with auth + role checking
- [x] 2.2 Create `shared/components/ForbiddenPage.tsx` for 403 access denied
- [x] 2.3 Export from `shared/components/index.ts`

## 3. Router Integration

- [x] 3.1 Refactor `router.tsx` to use ProtectedRoute for protected routes
- [x] 3.2 Ensure login, register, public catalog routes remain unprotected
- [x] 3.3 Update App.tsx if needed for new route structure
