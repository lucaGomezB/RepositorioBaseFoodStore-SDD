## Why

El proyecto tiene 251 tests en backend que pasan, pero cero tests en frontend y sin metricas de cobertura. Ademas hay tech debt acumulado: deprecation warnings residuales, configuraciones de produccion pendientes y un script de integracion E2E que no forma parte del pipeline de tests. Completar la suite de testing y hacer polish final prepara el proyecto para produccion.

## What Changes

- Configurar Vitest en frontend con tests para componentes clave (authStore, cartStore, ProtectedRoute)
- Agregar frontend tests para: carrito (Zustand store), perfil (TanStack Query hooks), admin (MetricasPage)
- Agregar cobertura de codigo (pytest-cov para backend, istanbul/nyc para frontend)
- Integrar el E2E test como parte del pipeline (no script suelto)
- Agregar test_user.py faltante (esquema BD sincronizado ahora)
- Agregar configuracion de pre-commit hooks (ruff, tsc --noEmit)
- Agregar .env.example completo con todas las variables documentadas
- Verificar que el build de produccion funciona (npm run build, uvicorn)

## Capabilities

### New Capabilities
- `frontend-testing`: Tests unitarios y de integracion para el frontend con Vitest
- `coverage-report`: Generacion de reportes de cobertura para backend y frontend
- `ci-pipeline`: Configuracion basica para CI (lint, typecheck, tests, build)

### Modified Capabilities
Ninguna. Los requerimientos funcionales no cambian.

## Impact

- `frontend/package.json`: nueva dependencia vitest, @testing-library/react
- `frontend/src/`: tests en entidades, features y pages
- `backend/pyproject.toml`: pytest-cov si no esta configurado
- Nuevo: `.pre-commit-config.yaml` o script de pre-commit
- `.env.example`: actualizado con todas las variables
