# Guion de Presentacion — Food Store v5.0

**Duracion estimada**: 8-12 minutos
**Formato**: Demostracion en vivo + pantallazos de codigo

---

## Escena 1: Introduccion (30s)

> Mostrar: Pantalla de inicio del proyecto, terminal con `openspec list`

"Bienvenidos a Food Store, un sistema de e-commerce para gestion de pedidos de comida desarrollado con React, FastAPI y PostgreSQL. El proyecto sigue la metodologia Spec-Driven Development (SDD) con 39 cambios implementados y archivados desde la infraestructura base hasta el polish final. Actualmente contamos con 254 tests en backend, 81 tests en frontend, y una cobertura de codigo del 84%."

---

## Escena 2: Arquitectura del Backend (2 min)

> Mostrar: Estructura de directorios `backend/app/`

### 2a. Capas y flujo de dependencias (1 min)

"El backend sigue una arquitectura en capas con flujo unidireccional: Router → Service → Unit of Work → Repository → Model."

```
Router (HTTP) -> Service (logica) -> UoW (transaccion) -> Repository (datos) -> Model (SQLModel)
```

"Los routers son capa fina de HTTP, los services tienen la logica de negocio, el Unit of Work gestiona las transacciones atomicas, los repositorios acceden a datos, y los modelos definen las tablas."

> Mostrar: `backend/app/api/pedidos.py` - codigo del router

### 2b. Unit of Work en accion (1 min)

> Mostrar: `backend/app/core/uow.py` y un endpoint que lo usa

"Aqui vemos el Unit of Work en accion. Cada endpoint que escribe datos abre un contexto `with UnitOfWork(session) as uow:`. Al entrar, se inicia una transaccion. Al salir sin errores, se hace commit automatico. Si hay una excepcion, se hace rollback."

```python
@router.post("/", response_model=PedidoRead, status_code=201)
def crear_pedido(data: CrearPedidoRequest, session: Session = Depends(get_db)):
    try:
        with UnitOfWork(session) as uow:
            pedido = PedidoService.crear_pedido(uow, ...)
        return pedido
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

"Ningun service hace session.commit() directo — el UoW lo maneja."

### 2c. Modulos por dominio (30s)

> Mostrar: `backend/app/domain/` con sus subdirectorios

"Los modulos estan organizados por dominio: auth, usuarios, productos, categorias, pedidos, pagos, direcciones, admin. Cada modulo contiene su service, repository (si aplica) y schemas. Los modelos SQLModel estan centralizados en `app/models/`."

---

## Escena 3: Modelo de Datos (1 min)

> Mostrar: `backend/app/models/pedido.py` y `detalle_pedido.py`

"El modelo de datos sigue Tercera Forma Normal con 16 tablas. Aplicamos patrones como:"

- **Soft delete**: campo `eliminado_en` en lugar de DELETE fisico
- **Snapshots**: `nombre_snapshot` y `precio_snapshot` en DetallePedido preservan valores historicos
- **Precision Decimal**: todos los precios usan `Numeric(10,2)` — jamas float

```python
class DetallePedido(SQLModel, table=True):
    nombre_snapshot: str = Field(max_length=255)
    precio_snapshot: Decimal = Field(sa_column=Column(Numeric(10, 2)))
    subtotal: Decimal = Field(sa_column=Column(Numeric(10, 2)))
```

---

## Escena 4: Maquina de Estados - Pedidos (1 min)

> Mostrar: `backend/app/domain/pedidos/service.py` - TRANSICIONES

"Los pedidos siguen una maquina de estados finitos con 6 estados y transiciones estrictamente controladas."

```
PENDIENTE -> CONFIRMADO -> EN_PREPARACION -> EN_CAMINO -> ENTREGADO
    |             |              |
    +-> CANCELADO +-> CANCELADO  +-> CANCELADO (solo ADMIN)
```

"Cada transicion se valida contra el mapa de transiciones permitidas. Los estados ENTREGADO y CANCELADO son terminales. El historial de cambios es append-only: solo INSERT, nunca UPDATE ni DELETE."

> Mostrar: Transicion CONFIRMADO a EN_PREPARACION con restauracion de stock al cancelar

---

## Escena 5: Autenticacion y RBAC (1 min)

> Mostrar: `backend/app/core/auth/` y un endpoint protegido

"La autenticacion usa JWT con access token (30 min) y refresh token (7 dias) con rotacion. Al hacer logout, el refresh token se revoca en base de datos."

"El control de acceso tiene 4 roles:"

| Rol | Permisos |
|-----|----------|
| ADMIN | CRUD completo, metricas, configuracion |
| STOCK | Catalogo, productos, stock, ingredientes |
| PEDIDOS | Ver y avanzar pedidos, historial |
| CLIENT | Catalogo, carrito, mis pedidos |

> Mostrar: `require_roles([Role.ADMIN, Role.STOCK])` en un endpoint

"El rate limiting en login protege contra fuerza bruta: maximo 5 intentos por IP cada 15 minutos."

---

## Escena 6: Frontend - Feature-Sliced Design (1 min)

> Mostrar: `frontend/src/` estructura FSD

"El frontend sigue Feature-Sliced Design con 5 capas: app, pages, features, entities, shared. Los imports fluyen de arriba hacia abajo."

### Zustand stores (30s)

> Mostrar: `frontend/src/shared/stores/`

"El estado del cliente se gestiona con 4 stores de Zustand:"

| Store | Estado | Persiste |
|-------|--------|----------|
| authStore | tokens JWT, usuario | localStorage |
| cartStore | items del carrito | localStorage |
| paymentStore | estado del pago | no |
| uiStore | modales, sidebar | no |

"El estado del servidor se maneja exclusivamente con TanStack Query. Nunca se mezclan ambos tipos de estado."

---

## Escena 7: Funcionalidades Cliente (1 min 30s)

> Mostrar: Pantallazos de la aplicacion funcionando

### 7a. Catalogo de productos (30s)

"El catalogo publico muestra productos con disponibilidad, filtro por categoria y busqueda por nombre. Incluye skeleton loaders mientras carga y paginacion."

### 7b. Carrito de compras (30s)

"El carrito es client-side con persistencia en localStorage. Permite agregar/quitar items, personalizar ingredientes, y muestra subtotales en tiempo real."

### 7c. Creacion de pedido (30s)

"Al crear un pedido, todo ocurre en una sola transaccion atomica: se validan stocks, se toman snapshots de precios, se calculan totales, y se registra la transicion inicial en el historial. Si algo falla, nada persiste."

---

## Escena 8: Panel de Administracion (1 min)

> Mostrar: Pantallazos del admin

"El panel de administracion incluye:"

- **Dashboard**: KPIs, graficos de ventas con recharts, distribucion de pedidos
- **Productos**: CRUD completo con categorias e ingredientes
- **Pedidos**: Vista de todos los pedidos, transiciones de estado, cancelaciones
- **Usuarios**: CRUD con asignacion de roles RBAC
- **Stock**: Vista de productos con stock bajo, actualizacion masiva

---

## Escena 9: Testing y Documentacion (1 min)

> Mostrar: Terminal ejecutando tests

### Backend

```bash
cd backend
pytest  # 254 tests, 0 failures
pytest --cov=app --cov-report=html  # cobertura 84%
```

### Frontend

```bash
cd frontend
npx vitest run  # 81 tests, 10 test files
npx tsc --noEmit  # TypeScript clean
npm run build  # build exitoso
```

### Documentacion API

> Mostrar: Navegador en http://localhost:8000/docs

"La API esta documentada via OpenAPI/Swagger en /docs y ReDoc en /redoc. Todos los endpoints tienen response_model, description, status_code explicito y ejemplos en los schemas."

---

## Escena 10: Cierre (30s)

"Food Store v5.0 implementa los 39 cambios planificados con 254 tests backend, 81 tests frontend, 84% de cobertura, y una arquitectura en capas con Unit of Work, precios Decimal y modulos por dominio.

El codigo fuente esta disponible en el repositorio publico con instrucciones de setup en el README."

---

## Checklist de pantallazos (CE-12)

1. `backend/app/api/` — Routers HTTP
2. `backend/app/domain/` — Modulos feature-first
3. `backend/app/core/uow.py` — Unit of Work en accion
4. `backend/app/models/` — Modelo con Decimal y snapshots
5. Catalogo de productos (frontend)
6. Carrito de compras con items
7. Detalle de pedido con historial de estados
8. Panel admin - Dashboard con graficos
9. Swagger UI en /docs
10. Terminal con `pytest` (254 passed)

---

## Notas para la grabacion

- Usar `git log --oneline --reverse` para mostrar el historial de 39 changes
- Para el backend, tener `uvicorn app.main:app` corriendo
- Para el frontend, tener `npm run dev` corriendo
- Tener datos de seed cargados (productos, categorias, ingredientes)
- Tener un par de pedidos creados para mostrar el historial de estados
- Tener un usuario admin y un cliente creados para mostrar RBAC
- Las tarjetas de prueba de MercadoPago estan en docs/Integrador.txt seccion 8.3
