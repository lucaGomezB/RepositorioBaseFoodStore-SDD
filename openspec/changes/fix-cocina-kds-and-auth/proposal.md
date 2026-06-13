## Why

The Cocina KDS backend uses PostgreSQL-specific raw SQL (`EXTRACT(EPOCH ...)`, `LEFT JOIN LATERAL`) in `listar_pedidos_con_tiempo()` that crashes on SQLite test databases. The test suite mocks a method name (`get_tiempo_en_cocina`) that does not exist on the repository, making test patches no-ops and giving false confidence. Separately, the Metricas page requires ADMIN role -- a known constraint that should be documented alongside the route definition.

## What Changes

- Rewrite `CocinaRepository.listar_pedidos_con_tiempo()` using SQLAlchemy ORM with portable datetime arithmetic (no raw SQL)
- Fix all `@patch` targets in `test_cocina.py` from `get_tiempo_en_cocina` to `listar_pedidos_con_tiempo`
- Add inline comment documenting the ADMIN-only requirement on the Metricas route

## Capabilities

### New Capabilities
None. No new capabilities introduced.

### Modified Capabilities
- `kds-kitchen-display`: Internal query implementation changes from raw SQL to ORM. External contract (return dict of pedido_id -> tiempo_segundos) remains identical. No spec-level requirement changes -- the delta is purely implementation.

## Impact

| Area | Impact | Description |
|------|--------|-------------|
| `backend/app/domain/cocina/repository.py` | Modified | Refactor `listar_pedidos_con_tiempo` to ORM |
| `backend/tests/api/test_cocina.py` | Modified | Fix 8 `@patch` targets |
| `backend/app/domain/cocina/service.py` | None | No changes needed |
| `frontend/src/app/router.tsx` | Modified | Add inline doc comment on Metricas ADMIN role |
