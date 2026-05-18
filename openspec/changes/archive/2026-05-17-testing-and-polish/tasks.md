## 1. Frontend testing setup

- [x] 1.1 Instalar vitest, @testing-library/react, @testing-library/jest-dom, jsdom
- [x] 1.2 Configurar vitest en frontend/vite.config.ts con jsdom environment
- [x] 1.3 Agregar script "test" en frontend/package.json
- [x] 1.4 Crear setup de tests con Testing Library (setupTests.ts)

## 2. Zustand store tests

- [x] 2.1 Test: authStore (login, logout, token management)
- [x] 2.2 Test: cartStore (addItem, removeItem, clearCart, addExclusion, exclusiones as number[])
- [x] 2.3 Test: paymentStore y uiStore (estados basicos)

## 3. TanStack Query hook tests

- [x] 3.1 Test: usePerfil hook con mocks de API
- [x] 3.2 Test: usePedidos hook con paginacion
- [x] 3.3 Test: useAdminPedidos hook con filtros

## 4. Page component tests

- [x] 4.1 Test: MetricasPage renderiza KPIs con mock data
- [x] 4.2 Test: MisPedidosPage renderiza lista de pedidos
- [x] 4.3 Test: PedidoDetailPage renderiza timeline de estados

## 5. Backend coverage

- [x] 5.1 Instalar/verificar pytest-cov
- [x] 5.2 Agregar script de coverage en backend (Makefile con pytest --cov=app --cov-report=html)
- [x] 5.3 Verificar cobertura actual y reportar gaps (84% total)
- [x] 5.4 Agregar tests E2E para flujo completo (3 nuevos en test_e2e_flow.py)
- [x] 6.1 Migrar a test de pytest con fixture database (test_e2e_flow.py creado)
- [x] 6.2 Agregar al pipeline de tests (corre con pytest tests/)

## 7. Pre-commit hooks

- [x] 7.1 Agregar .pre-commit-config.yaml con ruff + tsc --noEmit
- [x] 7.2 Instalar pre-commit y verificar que funciona

## 8. .env.example

- [x] 8.1 Revisar backend/app/core/config.py y .env real
- [x] 8.2 Actualizar backend/.env.example con todas las variables documentadas (agregadas RATE_LIMIT_*)
- [x] 8.3 Actualizar frontend/.env.example (agregadas VITE_MP_PUBLIC_KEY, VITE_LOGIN_USER, VITE_LOGIN_PASS)

## 9. Final verification

- [x] 9.1 Ejecutar pytest (254 passed, 0 failed)
- [x] 9.2 Ejecutar frontend tests (81 passed, 10 test files)
- [x] 9.3 Ejecutar npx tsc --noEmit (clean, no errors)
- [x] 9.4 Ejecutar npm run build (builds successfully)
