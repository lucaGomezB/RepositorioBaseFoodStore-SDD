## 1. Backend - endpoints de metricas

- [x] 1.1 Crear backend/app/api/admin.py con 4 endpoints protegidos (solo ADMIN)
- [x] 1.2 Endpoint GET /admin/metricas/resumen: total ventas, pedidos x estado, usuarios, top 5 productos
- [x] 1.3 Endpoint GET /admin/metricas/ventas: ventas agrupadas por dia/semana/mes con filtro fechas
- [x] 1.4 Endpoint GET /admin/metricas/productos-top: ranking productos mas vendidos
- [x] 1.5 Endpoint GET /admin/metricas/pedidos-por-estado: distribucion de pedidos por estado
- [x] 1.6 Registrar router en __init__.py

## 2. Frontend - pagina de metricas

- [x] 2.1 Instalar recharts
- [x] 2.2 Crear MetricasPage.tsx con: KPIs (tarjetas), LineChart ventas, BarChart top productos, PieChart estados
- [x] 2.3 Agregar ruta /metricas ADMIN-only en router
- [x] 2.4 Crear entities/metricas/api.ts con hooks TanStack Query
