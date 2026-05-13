## 1. Backend - paginacion y filtros

- [x] 1.1 Agregar paginacion (skip/limit) y filtro por estado a GET /pedidos
- [x] 1.2 Agregar filtros avanzados para admin (fecha desde/hasta, busqueda por cliente)

## 2. Frontend entities

- [x] 2.1 Crear entities/order/model.ts con tipos PedidoRead, PedidoDetail, PedidoFilters
- [x] 2.2 Crear entities/order/api.ts con hooks usePedidos, usePedido, usePedidoHistorial

## 3. Frontend pages

- [x] 3.1 Crear pages/MisPedidosPage.tsx (lista para CLIENT)
- [x] 3.2 Crear pages/PedidoDetailPage.tsx (detalle con timeline)
- [x] 3.3 Crear pages/PanelPedidosPage.tsx (panel para PEDIDOS/ADMIN con filtros)

## 4. Router

- [x] 4.1 Agregar rutas /mis-pedidos, /mis-pedidos/:id, /panel-pedidos
