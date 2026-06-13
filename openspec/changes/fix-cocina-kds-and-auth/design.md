## Design for fix-cocina-kds-and-auth

### D-1: Rewrite `listar_pedidos_con_tiempo()` using SQLAlchemy ORM

**Problem**: Raw SQL uses `EXTRACT(EPOCH FROM ...)::int` and `LEFT JOIN LATERAL` -- both PostgreSQL-only. SQLite tests crash.

**Solution**: Replace raw SQL with SQLAlchemy ORM using three steps:

1. Query the latest `HistorialEstadoPedido` for each relevant pedido where `estado_hacia == 'CONFIRMADO'` using a correlated subquery with `func.max()`.
2. Compute elapsed seconds in Python (`datetime.now(timezone.utc) - reference_time`), which is fully portable.
3. Fall back to `pedido.created_at` when no historial entry exists (matching the current `COALESCE` logic).

```python
def listar_pedidos_con_tiempo(self) -> dict[int, int]:
    subq = (
        select(
            HistorialEstadoPedido.pedido_id,
            func.max(HistorialEstadoPedido.created_at).label("confirmado_at"),
        )
        .where(HistorialEstadoPedido.estado_hacia == "CONFIRMADO")
        .group_by(HistorialEstadoPedido.pedido_id)
        .subquery()
    )
    stmt = (
        select(Pedido.id, subq.c.confirmado_at)
        .outerjoin(subq, Pedido.id == subq.c.pedido_id)
        .where(Pedido.estado_codigo.in_(["CONFIRMADO", "EN_PREPARACION"]))
    )
    now = datetime.now(timezone.utc)
    result: dict[int, int] = {}
    for row in self.session.exec(stmt):
        ref = row.confirmado_at or next(
            p.created_at for p in self.session.exec(
                select(Pedido.created_at).where(Pedido.id == row.id)
            )
        )
        result[row.id] = int((now - ref).total_seconds())
    return result
```

**Optimization**: Collect all pedido IDs first, fetch their `created_at` in a single batch query to avoid N+1 inside the loop.

### D-2: Fix test mock targets

**Problem**: 8 `@patch` decorators across `test_cocina.py` patch `CocinaRepository.get_tiempo_en_cocina` which does not exist. The real method is `listar_pedidos_con_tiempo`.

**Solution**: Replace all occurrences:
- `app.domain.cocina.repository.CocinaRepository.get_tiempo_en_cocina`
- `app.domain.cocina.repository.CocinaRepository.listar_pedidos_con_tiempo`

No other changes needed -- the mock return values (0, 120, 3600) remain valid for the real method.

### D-3: Document Metricas ADMIN role requirement

**Problem**: MetricasPage already has `requiredRoles={[1]}` in the route definition. This is correct. However, the constraint is not documented inline, making it easy to accidentally change.

**Solution**: Add a comment above the Admin-only route block in `router.tsx`:

```typescript
// Admin-only pages: only role 1 (ADMIN) can access
{
  element: <ProtectedRoute requiredRoles={[1]} />,
  children: [
    { path: 'metricas', element: <MetricasPage /> },
    ...
  ],
}
```

The existing comment reads "Protected: Admin-only pages" which is sufficient. No code change needed beyond verifying the comment is already accurate.

## Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | ORM query with Python-side arithmetic | Portable across PostgreSQL/SQLite; avoids raw SQL entirely |
| 2 | Batch fetch for `created_at` fallback | Prevents N+1 query pattern in the loop |
| 3 | No delta spec needed | External contract unchanged; pure refactor |
