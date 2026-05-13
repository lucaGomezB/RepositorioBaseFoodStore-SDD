## 1. Frontend testing setup

- [ ] 1.1 Instalar vitest, @testing-library/react, @testing-library/jest-dom, jsdom
- [ ] 1.2 Configurar vitest en frontend/vite.config.ts con jsdom environment
- [ ] 1.3 Agregar script "test" en frontend/package.json
- [ ] 1.4 Crear setup de tests con Testing Library (setupTests.ts)

## 2. Zustand store tests

- [ ] 2.1 Test: authStore (login, logout, token management)
- [ ] 2.2 Test: cartStore (addItem, removeItem, clearCart, addExclusion, exclusiones as number[])
- [ ] 2.3 Test: paymentStore y uiStore (estados basicos)

## 3. TanStack Query hook tests

- [ ] 3.1 Test: usePerfil hook con mocks de API
- [ ] 3.2 Test: usePedidos hook con paginacion
- [ ] 3.3 Test: useAdminPedidos hook con filtros

## 4. Page component tests

- [ ] 4.1 Test: MetricasPage renderiza KPIs con mock data
- [ ] 4.2 Test: MisPedidosPage renderiza lista de pedidos
- [ ] 4.3 Test: PedidoDetailPage renderiza timeline de estados

## 5. Backend coverage

- [ ] 5.1 Instalar/verificar pytest-cov
- [ ] 5.2 Agregar script de coverage en backend (pytest --cov=app --cov-report=html)
- [ ] 5.3 Verificar cobertura actual y reportar gaps
- [ ] 5.4 Agregar tests faltantes para endpoints sin cobertura

## 6. E2E test integration

- [ ] 6.1 Migrar _integration_test.py a test de pytest (fixture database)
- [ ] 6.2 Agregar al pipeline de tests (pytest tests/ - no suelto)

## 7. Pre-commit hooks

- [ ] 7.1 Agregar .pre-commit-config.yaml con ruff + tsc --noEmit
- [ ] 7.2 Instalar pre-commit y verificar que funciona

## 8. .env.example

- [ ] 8.1 Revisar backend/app/core/config.py y .env real
- [ ] 8.2 Actualizar backend/.env.example con todas las variables documentadas
- [ ] 8.3 Actualizar frontend/.env.example si falta documentacion

## 9. Final verification

- [ ] 9.1 Ejecutar pytest (tests existentes + nuevos)
- [ ] 9.2 Ejecutar frontend tests (npx vitest run)
- [ ] 9.3 Ejecutar npx tsc --noEmit
- [ ] 9.4 Ejecutar npm run build
