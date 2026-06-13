## 1. Rewrite Cocina Repository Query

- [x] 1.1 Replace raw SQL in `listar_pedidos_con_tiempo()` with SQLAlchemy ORM query using `func.max()` correlated subquery for `HistorialEstadoPedido`

- [x] 1.2 Compute elapsed seconds in Python using `datetime.now(timezone.utc)` arithmetic instead of `EXTRACT(EPOCH FROM ...)` to ensure SQLite compatibility

- [x] 1.3 Batch-fetch `Pedido.created_at` fallback values in a single query to avoid N+1 inside the loop

## 2. Fix Cocina Test Mock Targets

- [x] 2.1 Replace all 8 `@patch("app.domain.cocina.repository.CocinaRepository.get_tiempo_en_cocina")` with `@patch("app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo")` in `test_cocina.py`

## 3. Run and Verify Tests

- [x] 3.1 Run `pytest backend/tests/api/test_cocina.py -v` and confirm all tests pass

- [x] 3.2 Verify no regressions in the broader test suite: `pytest backend/ -x --tb=short` (304 passed, 7 pre-existing failures unrelated)

## 4. Document Metricas ADMIN Role

- [x] 4.1 Verify the Metricas route comment in `frontend/src/app/router.tsx` already documents the ADMIN-only constraint ("Protected: Admin-only pages")

- [x] 4.2 Update comment to explicitly state "role 1 (ADMIN) required"
