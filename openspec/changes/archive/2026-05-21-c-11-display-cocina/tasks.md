## 1. Backend — Rol COCINA y seed (US-COCINA-04)

- [x] 1.1 Agregar `COCINA = 5` al enum `Role` en `backend/app/core/auth/roles.py`
- [x] 1.2 Agregar seed del rol `COCINA` (id=5) y usuario `cocina@foodstore.com` en `backend/app/db/seed.py`
- [x] 1.3 Agregar `COCINA` a `require_roles` en `PATCH /pedidos/{id}/estado` en `backend/app/api/pedidos.py`

## 2. Backend — Infraestructura de tiempo real

- [x] 2.1 Crear `backend/app/core/websocket/__init__.py` con `ConnectionManager` (singleton, set de conexiones asyncio)
- [x] 2.2 Implementar `manager.py` con métodos `connect()`, `disconnect()`, `broadcast()` con manejo de concurrencia
- [x] 2.3 Crear `backend/app/core/websocket/events.py` con tipos de eventos (dataclass o TypedDict)

## 3. Backend — Módulo cocina/ (domain)

- [x] 3.1 Crear `backend/app/domain/cocina/__init__.py`
- [x] 3.2 Crear `backend/app/domain/cocina/schemas.py` con schemas de request/response para el KDS
- [x] 3.3 Crear `backend/app/domain/cocina/repository.py` con consultas: listar pedidos CONFIRMADO + EN_PREPARACION ordenados por antigüedad
- [x] 3.4 Crear `backend/app/domain/cocina/service.py` con lógica de visualización del KDS

## 4. Backend — API de cocina (REST + WebSocket)

- [x] 4.1 Crear `backend/app/api/cocina.py` con `GET /api/v1/cocina/pedidos` (REST, carga inicial y fallback)
- [x] 4.2 Agregar `WS /api/v1/cocina/ws` con auth JWT en handshake y registro en ConnectionManager
- [x] 4.3 Registrar router de cocina en la aplicación FastAPI (main.py o api/__init__.py)

## 5. Backend — Eventos desde el FSM

- [x] 5.1 Modificar `PedidoService.transicionar_estado()` para aceptar `rol_id` como parámetro opcional
- [x] 5.2 Publicar eventos según la transición: PEDIDO_CONFIRMADO, PEDIDO_EN_PREPARACION, PEDIDO_EN_CAMINO, PEDIDO_CANCELADO
- [x] 5.3 Agregar validación de transiciones por rol (RN-CO03): COCINA solo CONFIRMADO→EN_PREPARACION y EN_PREPARACION→EN_CAMINO; otras transiciones devuelven 403
- [x] 5.4 Modificar webhook IPN de pagos para emitir PEDIDO_CONFIRMADO al aprobar pago

## 6. Frontend — Feature cocina/ (hooks y componentes)

- [x] 6.1 Crear `frontend/src/features/cocina/types.ts` con tipos de datos del KDS
- [x] 6.2 Crear hook `frontend/src/features/cocina/hooks/useCocinaWS.ts` con WebSocket + polling fallback (30s)
- [x] 6.3 Crear componente `frontend/src/features/cocina/components/KDSColumn.tsx` (columna de estado)
- [x] 6.4 Crear componente `frontend/src/features/cocina/components/KDSCard.tsx` (tarjeta de pedido con botones de acción)
- [x] 6.5 Crear componente `frontend/src/features/cocina/components/UrgencyTimer.tsx` (timer con 3 umbrales, recálculo cada 15s)
- [x] 6.6 Implementar alerta sonora (Web Audio API) y flash visual al recibir PEDIDO_CONFIRMADO, con toggle persistente (US-COCINA-05)

## 7. Frontend — Página KDS y navegación

- [x] 7.1 Crear `frontend/src/pages/CocinaPage.tsx` con layout de dos columnas ("Por preparar" / "En preparación")
- [x] 7.2 Agregar ruta `/cocina` con guard de rol (COCINA, PEDIDOS, ADMIN)
- [x] 7.3 Excluir ruta `/cocina` de auto-logout por inactividad — NOTA: no existe auto-logout en el proyecto aún, se agregó comentario TODO
- [x] 7.4 Agregar enlace a `/cocina` en la navegación para roles autorizados

## 8. Verificación y cierre

- [x] 8.1 Escribir tests unitarios del service de cocina
- [x] 8.2 Escribir tests de integración del WebSocket (TestClient de FastAPI)
- [x] 8.3 Escribir tests del seed (rol COCINA existe, usuario de prueba existe)
- [x] 8.4 Ejecutar `judgment-day` para revisión adversarial del change — APROBADO ✅
- [x] 8.5 Archivar el change con `/opsx:archive c-11-display-cocina`
