## Context

Backend tiene 251 tests en 16 archivos, todos pasando. Frontend tiene 0 tests. No hay cobertura configurada, no hay CI, no hay pre-commit hooks. El E2E test existe como script standalone fuera del pipeline.

## Goals / Non-Goals

**Goals:**
- Configurar Vitest + Testing Library en frontend
- Tests minimos para: Zustand stores (cart, auth), hooks TanStack Query, paginas principales, componentes compartidos
- Configurar pytest-cov para backend con minimo 80%
- Integrar E2E test como test de pytest (no script suelto)
- Pre-commit hooks: ruff (lint) + tsc --noEmit + pytest
- .env.example completo y documentado

**Non-Goals:**
- No cubrir cada componente individual (solo los criticos)
- No configurar CI/CD completo (solo scripts locales)
- No integration tests de frontend con backend real (el E2E test ya cubre eso)

## Decisions

### 1. Vitest sobre Jest
**Decision**: Usar Vitest que ya viene con Vite (configuracion zero). Testing Library para componentes React.

**Razon**: El proyecto ya usa Vite. Vitest es compatible nativo, mas rapido y no requiere configuracion adicional.

### 2. Tests priorizados por riesgo
**Decision**: Testear en orden: stores Zustand (logica pura) > hooks TanStack Query (integracion) > paginas (rendering) > componentes compartidos (UI).

**Razon**: Las stores tienen la logica de negocio del frontend. Si fallan, falla todo. Los componentes UI son mas estables.

### 3. pytest-cov con --cov-report=html
**Decision**: Usar pytest-cov con reporte HTML y terminal. Minimo 80% en backend.

**Razon**: El backend ya tiene buena cobertura, verificar el porcentaje da visibilidad.

### 4. E2E test como fixture de pytest
**Decision**: Migrar el script _integration_test.py a un test de pytest con fixture de base de datos.

**Razon**: El script actual existe fuera del pipeline. Integrarlo a pytest permite que se ejecute en cada corrida de tests.

## Risks / Trade-offs

- **Riesgo**: Tests de frontend pueden ser lentos si se renderizan muchos componentes.
  - **Mitigacion**: Usar testing-library con queries semanticas, evitar snapshot testing.
- **Riesgo**: pre-commit hooks pueden ralentizar commits.
  - **Mitigacion**: Hooks ligeros (ruff, tsc --noEmit). Test pesados (pytest, frontend tests) solo en CI.
- **Riesgo**: pytest-cov puede fallar si el umbral no se cumple.
  - **Mitigacion**: Umbral inicial en 70%, subir gradualmente a 80%.
