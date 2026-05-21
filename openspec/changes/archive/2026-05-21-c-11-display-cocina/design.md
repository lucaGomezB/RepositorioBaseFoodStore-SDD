## Context

Food Store es un e-commerce de delivery con backend FastAPI + SQLModel + PostgreSQL y frontend React + TypeScript + Vite + Tailwind CSS. Actualmente es REST puro — no existe infraestructura de tiempo real.

El FSM de pedidos tiene 6 estados (PENDIENTE, CONFIRMADO, EN_PREPARACION, EN_CAMINO, ENTREGADO, CANCELADO) con sus transiciones definidas en `PedidoService.transicionar_estado()`. El RBAC tiene 4 roles (ADMIN, STOCK, PEDIDOS, CLIENT) definidos en `backend/app/core/auth/roles.py` como `IntEnum`.

Este change agrega:
- Un nuevo rol `COCINA` (id=5)
- Un módulo backend `cocina/` con lógica de KDS
- Infraestructura de tiempo real (pub/sub en proceso + WebSocket)
- Una página frontend `/cocina` con el display de cocina

## Goals / Non-Goals

**Goals:**
- Agregar el rol `COCINA` al sistema (enum, seed, require_roles)
- Implementar un KDS que muestre pedidos CONFIRMADO y EN_PREPARACION en tiempo real
- Permitir que el cocinero avance `CONFIRMADO → EN_PREPARACION` y `EN_PREPARACION → EN_CAMINO`
- Cada transición del cocinero queda auditada en `HistorialEstadoPedido`
- El KDS recibe eventos push sin recargar la página
- Resiliencia: si el WebSocket se cae, fallback a polling cada 30s
- Timer de urgencia visual (RN-CO07) con 3 umbrales
- Guard de ruta `/cocina` y exclusión de auto-logout

**Non-Goals:**
- No se agrega estado intermedio `LISTO` entre EN_PREPARACION y EN_CAMINO (PA-CO-01, diferido a v2)
- No se implementa US-COCINA-07 (marcar producto no disponible desde cocina)
- No hay multi-instancia ni Redis — la v1 funciona en single-instance
- No hay estaciones de cocina (BAR, GRILL, etc.)
- No cambia la forma del FSM — solo se agregan roles autorizados por transición

## Decisions

### D-1: WebSocket vs SSE
**Decisión: WebSocket.**

**Alternativa considerada:** SSE (Server-Sent Events) es más simple para push unidireccional servidor→cliente.

**Razón:** Aunque SSE sería suficiente para el caso de uso (solo push del servidor al KDS), WebSocket ofrece:
- Un solo protocolo para todas las necesidades futuras (el KDS podría necesitar enviar datos al servidor en v2, ej. notas internas de cocina)
- La librería `fastapi.WebSocket` está integrada en FastAPI, sin dependencias externas
- El `TestClient` de FastAPI soporta WebSocket para testing

**Tradeoff:** WebSocket requiere manejar reconexión explícita en el cliente (US-COCINA-08 lo cubre). SSE reconecta automáticamente vía `EventSource`.

### D-2: Pub/Sub en proceso (sin Redis)
**Decisión:** Usar un gestor de conexiones en proceso con `asyncio` (`set` de WebSocket connections + `asyncio.Queue` o broadcasting directo).

**Alternativa considerada:** Redis Pub/Sub + outbox pattern.

**Razón:** Food Store es single-instance en v1. El pub/sub en proceso es órdenes de magnitud más simple y no agrega dependencias de infraestructura. Cuando el sistema necesite multi-instancia, el reemplazo natural es Redis Pub/Sub sin cambiar la interfaz del gestor de conexiones (se abstrae detrás de un `EventBus`).

**Límite conocido:** En multi-instancia, el evento se publica en la instancia donde ocurre la transición. Si el cocinero está conectado a otra instancia, no recibe el evento. La migración a Redis resuelve esto.

### D-3: El rol COCINA se agrega como IntEnum existente
**Decisión:** `COCINA = 5` en `backend/app/core/auth/roles.py`.

**Alternativa considerada:** Usar un string enum como sugiere la skill (PK semántica `COCINA` en la tabla `roles`).

**Razón:** El modelo `Rol` actual usa `id: int` como PK, y el `Role` enum es `IntEnum`. Cambiar a VARCHAR implicaría migración de esquema y refactor de todo el sistema. Agregar id=5 es simple, consistente con el diseño actual, y no rompe nada existente.

**Impacto:** Los 4 roles existentes quedan igual. `COCINA` se agrega como nuevo registro en seed y en el enum.

### D-4: Códigos de estado — se usa `EN_PREPARACION` (existente)
**Decisión:** Usar `EN_PREPARACION` como código BD, no `EN_PREP`.

**Alternativa considerada:** La skill sugiere `EN_PREP` como código BD.

**Razón:** El seed existente ya define `EN_PREPARACION` como código del estado "En Preparación". Cambiarlo implicaría migración y afectaría datos existentes. La skill usa `EN_PREP` como abreviatura conceptual, pero el código real del proyecto es `EN_PREPARACION`.

### D-5: El gestor de conexiones se implementa como singleton en memoria
**Decisión:** Clase `ConnectionManager` con un `set` de `WebSocket` + `Lock` asyncio, registrada como dependencia de FastAPI.

**Razon:** Patrón simple y probado para single-instance. El `set` contiene las conexiones activas. Para broadcast, se itera sobre el set y se envía el mensaje a cada una, atrapando excepciones de conexiones caídas.

**Estructura sugerida:**
```
backend/app/core/websocket/
  __init__.py
  manager.py       # ConnectionManager (singleton)
  events.py        # Event type definitions
```

### D-6: La publicación de eventos se hace desde el service del FSM
**Decisión:** El `PedidoService.transicionar_estado()` recibe el `ConnectionManager` como dependencia opcional y, después de commitear la transición, publica el evento correspondiente.

**Alternativa considerada:** Usar un event dispatcher separado (event bus con suscriptores).

**Razón:** Para v1, la publicación directa desde el service es lo más simple y evita la sobre-ingeniería de un event bus. El service ya tiene toda la información necesaria (estado anterior, nuevo estado, pedido_id). Si se necesitan más consumidores en el futuro, se puede extraer un EventBus sin cambiar la lógica.

## Architecture

### Flujo de datos del KDS

```
                    ┌──────────────────────────────┐
                    │       Frontend (React)        │
                    │   ┌────────────────────────┐  │
                    │   │     CocinaPage.tsx      │  │
                    │   │  ┌──────────────────┐  │  │
                    │   │  │  useCocinaWS hook │  │  │
                    │   │  └────────┬─────────┘  │  │
                    │   │           │             │  │
                    │   │  ┌────────▼─────────┐  │  │
                    │   │  │  Columnas KDS     │  │  │
                    │   │  │ "Por preparar"    │  │  │
                    │   │  │ "En preparación"  │  │  │
                    │   │  └──────────────────┘  │  │
                    │   └────────────────────────┘  │
                    └──────────────┬────────────────┘
                WebSocket ◄────────┤──────── REST (fallback)
                                   │
              ┌────────────────────▼────────────────┐
              │         Backend (FastAPI)             │
              │                                      │
              │  ┌────────────────────────────────┐  │
              │  │  WS /api/v1/cocina/ws          │  │
              │  │  (auth JWT en handshake)       │  │
              │  └──────────────┬─────────────────┘  │
              │                 │                     │
              │  ┌──────────────▼─────────────────┐  │
              │  │  ConnectionManager             │  │
              │  │  (pub/sub en proceso)          │  │
              │  └──────────────┬─────────────────┘  │
              │                 │                     │
              │  ┌──────────────▼─────────────────┐  │
              │  │  GET /api/v1/cocina/pedidos    │  │
              │  │  (REST — carga inicial)         │  │
              │  └──────────────┬─────────────────┘  │
              │                 │                     │
              │  ┌──────────────▼─────────────────┐  │
              │  │  PedidoService                  │  │
              │  │  .transicionar_estado()         │  │
              │  │    → publica evento al          │  │
              │  │      ConnectionManager          │  │
              │  └────────────────────────────────┘  │
              │                                      │
              └──────────────────────────────────────┘
```

### Eventos publicados

| Evento | Disparador | Payload |
|--------|-----------|---------|
| `PEDIDO_CONFIRMADO` | PENDIENTE → CONFIRMADO | `{ pedido_id, items, created_at }` |
| `PEDIDO_EN_PREPARACION` | CONFIRMADO → EN_PREPARACION | `{ pedido_id }` |
| `PEDIDO_EN_CAMINO` | EN_PREPARACION → EN_CAMINO | `{ pedido_id }` |
| `PEDIDO_CANCELADO` | cualquier → CANCELADO en fase cocina | `{ pedido_id }` |

### Estructura de módulos

```
backend/app/
├── core/
│   ├── auth/
│   │   └── roles.py              # + COCINA = 5
│   └── websocket/                 # NUEVO
│       ├── __init__.py
│       ├── manager.py             # ConnectionManager
│       └── events.py              # Event types
├── domain/
│   └── cocina/                    # NUEVO
│       ├── __init__.py
│       ├── schemas.py             # KDS request/response schemas
│       ├── repository.py          # Consultas de pedidos para cocina
│       └── service.py             # Lógica del KDS
├── api/
│   ├── pedidos.py                 # + COCINA en require_roles del PATCH
│   └── cocina.py                  # NUEVO: REST + WS endpoints
└── db/
    └── seed.py                    # + Rol COCINA, + usuario cocina@foodstore.com

frontend/
├── src/
│   ├── features/
│   │   └── cocina/                # NUEVO
│   │       ├── hooks/
│   │       │   └── useCocinaWS.ts # WebSocket + polling fallback
│   │       ├── components/
│   │       │   ├── KDSColumn.tsx
│   │       │   ├── KDSCard.tsx
│   │       │   └── UrgencyTimer.tsx
│   │       └── types.ts
│   ├── pages/
│   │   └── CocinaPage.tsx          # NUEVO
│   └── app/
│       └── router.tsx              # + ruta /cocina con guard
```

## Risks / Trade-offs

- **[Performance]** Broadcasting a muchas pantallas de cocina desde un solo proceso puede saturar el event loop si hay +50 conexiones. → **Mitigación:** En v1, una cocina tiene 1-3 pantallas como máximo. Si escala, migrar a Redis Pub/Sub.
- **[Disponibilidad]** El pub/sub en proceso pierde eventos si no hay pantallas conectadas. → **Mitigación:** Es comportamiento esperado (best-effort). El KDS siempre puede hacer carga completa al reconectar. Documentado como límite conocido.
- **[Seguridad]** El WebSocket valida JWT en el handshake, pero el token podría expirar durante una conexión larga (turno de cocina). → **Mitigación:** Implementar renovación de token sobre WebSocket (mensaje de keepalive con nuevo token) o reconexión automática con refresh token.
- **[Consistencia]** El estado del KDS es eventualmente consistente con la BD. → **Mitigación:** Aceptable para un display operativo. El cocinero siempre puede recargar manualmente (F5).
- **[FSM existente]** El endpoint `PATCH /pedidos/{id}/estado` actualmente solo permite ADMIN/PEDIDOS. Agregar COCINA requiere validación adicional en el service (RN-CO03: solo 2 transiciones). → **Mitigación:** La validación de transiciones por rol se implementa en el service, no solo en `require_roles`.
