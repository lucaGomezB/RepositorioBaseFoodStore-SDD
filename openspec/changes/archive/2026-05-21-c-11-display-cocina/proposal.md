## Why

Food Store actualmente **no tiene display de cocina ni rol cocinero**. El RBAC tiene solo 4 roles (ADMIN, STOCK, PEDIDOS, CLIENT) y toda la operación de preparación está absorbida por el Gestor de Pedidos vía el FSM. No existe una pantalla dedicada que muestre los pedidos a preparar en tiempo real. Esto fuerza al equipo de cocina a usar el panel de pedidos general (con ruido de pedidos pendientes de pago, entregados, etc.) y a recargar manualmente para ver nuevos pedidos.

Este change implementa un **Kitchen Display System (KDS)** adaptado al modelo de delivery/e-commerce de Food Store, permitiendo que el cocinero reciba pedidos pagados en tiempo real y gestione su preparación sin recargar la pantalla.

## What Changes

- **Nuevo rol `COCINA` (Cocinero)**: rol operativo de solo lectura + avance de estado en fase de cocina. Sin CRUD. Se agrega al enum `Role` (id=5), al seed de roles y a la validación `require_roles`.
- **Nuevo módulo backend `cocina/`**: Service con lógica de visualización (listar pedidos CONFIRMADO + EN_PREPARACION ordenados por antigüedad), y endpoints REST + WebSocket.
- **Infraestructura de tiempo real**: Gestor de conexiones pub/sub en proceso (`asyncio`) para push de eventos a las pantallas de cocina conectadas. Sin Redis en v1 single-instance.
- **Endpoint `GET /api/v1/cocina/pedidos`**: carga inicial y fallback REST del KDS.
- **Endpoint `WS /api/v1/cocina/ws`**: WebSocket con auth JWT en handshake para actualizaciones en tiempo real.
- **Eventos en tiempo real** desde el FSM: `PEDIDO_CONFIRMADO`, `PEDIDO_EN_PREPARACION`, `PEDIDO_EN_CAMINO`, `PEDIDO_CANCELADO` se publican cuando ocurre la transición.
- **Pantalla KDS frontend** en `/cocina`: dos columnas ("Por preparar" / "En preparación"), tarjetas con timer de urgencia (RN-CO07), alerta visual/sonora (US-COCINA-05), y fallback a polling (US-COCINA-08).
- **Modificaciones al FSM existente**: el endpoint `PATCH /pedidos/{id}/estado` ahora acepta el rol `COCINA`, y el service valida por rol qué transiciones permite (RN-CO03: solo CONFIRMADO→EN_PREPARACION y EN_PREPARACION→EN_CAMINO).
- **Guard de ruta `/cocina`**: accesible para COCINA, PEDIDOS y ADMIN. Excluida de auto-logout por inactividad.

**No se excluye del scope:**
- Marcar producto como no disponible desde cocina (US-COCINA-07) — queda fuera de v1, solapa con rol STOCK.
- Estado intermedio `LISTO` entre EN_PREPARACION y EN_CAMINO (PA-CO-01) — diferido a v2.

## Capabilities

### New Capabilities
- `kds-kitchen-display`: Kitchen Display System — visualización en tiempo real de pedidos a preparar, con columnas por estado, timer de urgencia, y acciones de avance de estado.
- `real-time-events`: Infraestructura de eventos en tiempo real (pub/sub en proceso + WebSocket) para push de cambios de estado a pantallas conectadas.

### Modified Capabilities
- `rbac-authorization`: Se agrega el rol COCINA (id=5) con permisos de solo lectura sobre el KDS y avance de estado limitado a la fase de cocina.
- `payment-processing`: El flujo de pago aprobado (PENDIENTE → CONFIRMADO) ahora debe emitir un evento `PEDIDO_CONFIRMADO` hacia las pantallas de cocina.

## Impact

- **Backend**: Nuevo módulo `backend/app/domain/cocina/` (service, schemas, repository). Modificaciones en `backend/app/domain/pedidos/service.py` (FSM: agregar validación por rol, emitir eventos). Modificaciones en `backend/app/api/pedidos.py` (agregar COCINA a roles permitidos). Nuevo archivo `backend/app/core/websocket/` para el gestor de conexiones. Modificación en `backend/app/core/auth/roles.py` (agregar COCINA=5). Modificación en `backend/app/db/seed.py` (agregar seed de rol COCINA y usuario de prueba).
- **Frontend**: Nueva feature `frontend/src/features/cocina/` con hook WebSocket y lógica KDS. Nueva página `frontend/src/pages/CocinaPage.tsx`. Modificación en guards de ruta y navegación por rol.
- **Seed data**: Agregar `Rol(id=5, nombre='COCINA')` y usuario `cocina@foodstore.com`.
- **Arquitectura**: Se introduce una capa de tiempo real (pub/sub en proceso con `asyncio`) que no existía. Es un cambio unidireccional — el FSM publica eventos, el gestor de conexiones los distribuye.
