# Guion de Presentacion — Food Store

**Duracion estimada**: 7 minutos
**Formato**: Demostracion en vivo desde el frontend

---

## Escena 1: Introduccion (30s)

> Mostrar: `http://localhost:5173` — Home page con catalogo de productos

"Bienvenidos a **Food Store**, un sistema de e-commerce para gestión de pedidos de comida. Usa **React + TypeScript** en el frontend, **FastAPI + PostgreSQL** en el backend. Todo el proyecto se desarrolló con **Spec-Driven Development**: Primero la especificación, después el código. Somos Luca Gómez y Genaro Busto

---

## Escena 2: Demo Cliente — Catálogo y Carrito (1 min)

> Mostrar: Navegando el catálogo, filtrando por categoría, buscando

### 2a. Catálogo público (30s)

"El catálogo es público, no requiere login. Los productos se cargan con **skeleton loaders** y se pueden filtrar por categoría o buscar por nombre. La paginación es 1-based con paginado numérico."

> Mostrar: Agregar producto al carrito, abrir carrito, ver exclusiones de ingredientes

### 2b. Carrito de compras (30s)

"El carrito es **client-side con Zustand** y persiste en localStorage. Cada producto permite personalizar ingredientes (exclusiones) y el total se calcula en tiempo real. La sesión del carrito sobrevive a recargas y cierres del navegador."

---

## Escena 3: Demo Autenticación (1 min)

> Mostrar: Login en `/login` con credenciales admin@foodstore.com / admin123

### 3a. Login con httpOnly cookies (30s)

"El login usa **httpOnly cookies** — los tokens JWT nunca son accesibles desde JavaScript, lo que previene robo de tokens por XSS. Al recargar la página, la sesión se restaura automáticamente vía `GET /auth/me`."

> Mostrar: Sidebar filtrado por rol (admin ve todo)

### 3b. Menú por rol y M2M (30s)

"El sidebar se filtra según los **roles del usuario**. Un usuario puede tener múltiples roles simultáneamente gracias a la tabla pivote `UsuarioRol`. El menú muestra solo las opciones permitidas para los roles del usuario logueado."

---

## Escena 4: Demo Funcionalidades del Cliente (1 min 30s)

> Mostrar: Navegar a `/mis-pedidos`

### 4a. Mis pedidos (30s)

"Los clientes pueden ver sus pedidos con paginación, filtros por estado y fecha. Cada pedido muestra el detalle completo: items con snapshots de precio, historial de cambios de estado, dirección de entrega."

> Mostrar: `/direcciones` — agregar y editar dirección

### 4b. Direcciones de entrega (30s)

"La sección **Mis Direcciones** permite CRUD completo: crear, editar, eliminar y establecer una dirección como predeterminada. La primera dirección se marca automáticamente como predeterminada."

> Mostrar: Agregar producto al carrito, ir a checkout

### 4c. Checkout y pago (30s)

"Al hacer checkout, el pedido se crea en una **transacción atómica** usando Unit of Work: se validan stocks, se toman snapshots de precios y dirección, se registra el historial inicial. Si algo falla, nada persiste. El pago se integra con MercadoPago."

---

## Escena 5: Demo Panel de Administración (1 min 30s)

> Mostrar: `/metricas` — Dashboard con KPIs y gráficos

### 5a. Dashboard (30s)

"El panel administrativo tiene un dashboard con KPIs en tiempo real: total de ventas, pedidos por estado, productos más vendidos, usando **Recharts** para los gráficos."

> Mostrar: `/productos` — listado y edición, `/categorias`, `/ingredientes`

### 5b. Gestión de productos (30s)

"Catálogo completo: productos con categorías (jerárquicas) e ingredientes (con alérgenos). Stock actualizable desde la misma lista."

> Mostrar: `/usuarios` — modal de roles con checkboxes

### 5c. Usuarios y roles M2M (30s)

"La gestión de usuarios permite **asignar múltiples roles** mediante checkboxes: se pueden agregar o remover roles individualmente. Implementa **RN-RB04**: un ADMIN no puede auto-desasignarse si es el último administrador del sistema."

> Mostrar: `/panel-pedidos` — lista de pedidos, avanzar estado

### 5d. Gestión de pedidos (adicional si hay tiempo)

"Los gestores pueden ver todos los pedidos, avanzarlos por la máquina de estados finitos (PENDIENTE → CONFIRMADO → EN_PREPARACION → EN_CAMINO → ENTREGADO), con validación de transiciones y restauración de stock al cancelar."

---

## Escena 6: Testing y Documentación (30s)

> Mostrar: Terminal con `pytest` (254 passed) y `npx vitest run` (80 passed)

"**254 tests backend** con pytest, **80 tests frontend** con Vitest + Testing Library. TypeScript compila con **cero errores**. La API está documentada via **OpenAPI/Swagger** en `/docs` con ejemplos en todos los schemas."

---

## Escena 7: Puntos a Mejorar (30s)

> Mostrar: Pantalla en blanco o slide de cierre

"**Para una versión futura, los puntos a mejorar serían:**

- **Registro de usuarios**: el endpoint `POST /auth/register` ya existe, pero falta la página de registro en el frontend
- **Notificaciones en tiempo real**: webhooks o Server-Sent Events para actualizar el estado de pedidos sin recargar
- **Perfil de usuario**: la página de perfil permite editar datos, pero falta cambio de contraseña con confirmación
- **Responsive mobile**: la UI funciona en desktop, la adaptación mobile está incompleta
- **Internacionalización**: toda la UI está en español; agregar i18n para soporte multi-idioma"

---

## Resumen de métricas

| Métrica | Valor |
|---------|-------|
| Tests backend | 254 |
| Tests frontend | 80 |
| Cobertura | 84% |
| Roles | 4 (M2M) |
| Tablas | 16 + pivote |
| Cambios archivados | 40+ |

---

## Checklist de demostración

1. Home — catálogo con filtros y skeleton loaders
2. Login con httpOnly cookies + sidebar por rol
3. Carrito con exclusión de ingredientes
4. Mis pedidos — detalle con historial de estados
5. Direcciones — CRUD completo
6. Admin Dashboard — KPIs y gráficos
7. Productos — CRUD con categorías e ingredientes
8. Usuarios — asignación multi-rol con checkboxes
9. Panel de pedidos — transiciones de estado
10. Terminal — tests backend + frontend

---

## Notas técnicas

- Tener backend corriendo: `cd backend && .venv\Scripts\python -m uvicorn app.main:app --reload`
- Tener frontend corriendo: `cd frontend && npm run dev`
- Admin: `admin@foodstore.com` / `admin123`
- Stock: `stock@foodstore.com` . `stock123`
- Seed data cargada (10 productos, 10 categorías, 12 ingredientes)
- MercadoPago en modo test (tarjetas de prueba en docs/Integrador.txt sección 8.3)
