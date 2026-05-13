## 1. Error Boundary

- [x] 1.1 Create `shared/components/ErrorBoundary.tsx` as class component with componentDidCatch
- [x] 1.2 Export from `shared/components/index.ts`

## 2. Toast UI

- [x] 2.1 Create `shared/components/ToastContainer.tsx` that reads toasts from uiStore
- [x] 2.2 Style toasts with Tailwind: success (green), error (red), warning (yellow), info (blue)
- [x] 2.3 Export from `shared/components/index.ts`

## 3. HTTP Error Interceptor

- [x] 3.1 Create `shared/api/errorInterceptor.ts` with handleHttpError function
- [x] 3.2 Integrate error handler into httpClient response interceptor

## 4. Integration

- [x] 4.1 Add ErrorBoundary and ToastContainer to App.tsx or AppLayout.tsx
- [x] 4.2 Verify all toasts render correctly
