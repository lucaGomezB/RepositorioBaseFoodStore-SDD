# Changes Map — Food Store

## Overview

Mapa completo de 39 changes ordenados por dependencias reales para desarrollar Food Store v5.0.

**Referencia**: docs/Descripcion.txt, docs/Historias_de_usuario.txt, docs/Integrador.txt

---

## SPRINT 0 — INFRAESTRUCTURA

### 1. setup-monorepo-base ✅
**Funcionalidad**: Scaffolding del monorepo con estructura base (backend + frontend)
**Historias**: US-000
**Depende de**: Ninguna
**Estado**: Archivada (2026-04-28)

---

### 2. setup-backend-config
**Funcionalidad**: Configuración base del backend (FastAPI, SQLAlchemy, core modules)
**Historias**: US-000a
**Depende de**: setup-monorepo-base

---

### 3. setup-database-seed
**Funcionalidad**: PostgreSQL, Alembic, migraciones y seed data (Roles, EstadoPedido, FormaPago, Usuario admin)
**Historias**: US-000b
**Depende de**: setup-backend-config

---

### 4. setup-frontend-config
**Funcionalidad**: Configuración base del frontend (React, TypeScript, Vite, Tailwind, TanStack Query)
**Historias**: US-000c
**Depende de**: setup-monorepo-base

---

### 5. setup-backend-patterns
**Funcionalidad**: Patrones de infraestructura (BaseRepository[T], Unit of Work, dependencias FastAPI)
**Historias**: US-000d
**Depende de**: setup-database-seed

---

### 6. setup-zustand-stores
**Funcionalidad**: Cuatro stores Zustand tipados (authStore, cartStore, paymentStore, uiStore) con persist
**Historias**: US-000e
**Depende de**: setup-frontend-config

---

### 7. setup-error-handling
**Funcionalidad**: Manejo centralizado de errores (RFC 7807) + validación/sanitización de inputs
**Historias**: US-068, US-074
**Depende de**: setup-backend-config

---

### 8. setup-rate-limiting
**Funcionalidad**: slowapi middleware + rate limiting en login (5 intentos/15min)
**Historias**: US-073
**Depende de**: setup-backend-config

---

## EPIC 01 — AUTENTICACIÓN Y AUTORIZACIÓN

### 9. auth-login-register
**Funcionalidad**: Login con JWT, registro con bcrypt, asignación automática de rol CLIENT
**Historias**: US-001, US-002
**Depende de**: setup-backend-patterns, setup-zustand-stores

---

### 10. auth-token-refresh-logout
**Funcionalidad**: Refresh token con rotación, logout, invalidación en BD
**Historias**: US-003, US-004
**Depende de**: auth-login-register

---

### 11. auth-rbac-roles
**Funcionalidad**: Modelo RBAC, asignación de roles (ADMIN, STOCK, PEDIDOS, CLIENT), verificación per-endpoint
**Historias**: US-005, US-006
**Depende de**: auth-login-register

---

### 12. frontend-auth-guards
**Funcionalidad**: Route guards, interceptor 401 automático con refresh, protección de rutas
**Historias**: US-066, US-076
**Depende de**: auth-login-register, auth-rbac-roles

---

## EPIC 02 — NAVEGACIÓN Y LAYOUT

### 13. frontend-navigation-ui
**Funcionalidad**: Sidebar/navbar adaptado a rol, menú contextual
**Historias**: US-075
**Depende de**: frontend-auth-guards

---

### 14. frontend-error-handling
**Funcionalidad**: Error boundary global, toast/notification system
**Historias**: US-067
**Depende de**: setup-frontend-config

---

## EPIC 03 — CATÁLOGO DE PRODUCTOS

### 15. categories-hierarchical
**Funcionalidad**: CRUD categorías jerárquicas con FK autoreferencial, CTE recursivo
**Historias**: US-007, US-008, US-009, US-010
**Depende de**: setup-backend-patterns, auth-rbac-roles

---

### 16. ingredients-allergens
**Funcionalidad**: CRUD ingredientes con flag `es_alergeno`
**Historias**: US-011, US-012, US-013, US-014
**Depende de**: setup-backend-patterns, auth-rbac-roles

---

### 17. products-catalog-crud
**Funcionalidad**: CRUD productos con precio (NUMERIC), stock, disponibilidad
**Historias**: US-015, US-020, US-021, US-022
**Depende de**: categories-hierarchical, ingredients-allergens, auth-rbac-roles

---

### 18. products-associations
**Funcionalidad**: Asociación M2M productos↔categorías, productos↔ingredientes
**Historias**: US-016, US-017
**Depende de**: products-catalog-crud

---

### 19. products-public-catalog
**Funcionalidad**: GET /api/v1/productos con filtros, paginación, detalle completo
**Historias**: US-018, US-019, US-023
**Depende de**: products-associations

---

### 20. frontend-catalog-ui
**Funcionalidad**: Grid de productos con debounce/filtros/paginación, skeleton loaders
**Historias**: US-018, US-019, US-023
**Depende de**: products-public-catalog, frontend-error-handling

---

## EPIC 04 — GESTIÓN DEL PERFIL DEL CLIENTE

### 21. addresses-delivery
**Funcionalidad**: CRUD DireccionEntrega, marcar como predeterminada
**Historias**: US-024, US-025, US-026, US-027, US-028
**Depende de**: auth-login-register

---

### 22. user-profile
**Funcionalidad**: GET perfil propio, editar perfil, cambiar contraseña
**Historias**: US-061, US-062, US-063
**Depende de**: auth-login-register

---

### 23. frontend-profile-ui
**Funcionalidad**: Formularios de perfil, gestor de direcciones, cambio de contraseña
**Historias**: US-061, US-062, US-063, US-024, US-025, US-026, US-027, US-028
**Depende de**: addresses-delivery, user-profile

---

## EPIC 05 — CARRITO DE COMPRAS

### 24. cart-client-side
**Funcionalidad**: Carrito local en Zustand + localStorage, personalizaciones
**Historias**: US-029, US-030, US-031, US-032, US-033, US-034
**Depende de**: setup-zustand-stores, products-associations

---

### 25. frontend-cart-ui
**Funcionalidad**: CartDrawer/modal, agregar/quitar items, personalizar, resumen de totales
**Historias**: US-029, US-030, US-031, US-032, US-033, US-034
**Depende de**: cart-client-side, products-public-catalog

---

## EPIC 06 — PEDIDOS Y TRAZABILIDAD

### 26. orders-creation-fsm
**Funcionalidad**: Creación atómica de pedidos con UoW, snapshots, máquina de estados
**Historias**: US-035, US-036, US-037, US-038, US-039
**Depende de**: setup-backend-patterns, addresses-delivery, auth-rbac-roles

---

### 27. orders-state-transitions
**Funcionalidad**: Avanzar estado (PENDIENTE→CONFIRMADO→EN_PREP→EN_CAMINO→ENTREGADO), cancelación con restauración de stock
**Historias**: US-039, US-040, US-041, US-042, US-043, US-044
**Depende de**: orders-creation-fsm, products-catalog-crud

---

### 28. orders-history-audit-trail
**Funcionalidad**: Consultas del historial de estado, append-only validation
**Historias**: US-044
**Depende de**: orders-creation-fsm

---

### 29. frontend-orders-list-detail
**Funcionalidad**: Listado de pedidos, vista de detalle con historial timeline, filtros
**Historias**: US-049, US-050, US-051
**Depende de**: orders-state-transitions, orders-history-audit-trail

---

## EPIC 07 — PAGOS Y MERCADOPAGO

### 30. payments-mercadopago-integration
**Funcionalidad**: Creación de preferencia de pago, tokenización segura (PCI SAQ-A)
**Historias**: US-045
**Depende de**: orders-creation-fsm, setup-zustand-stores

---

### 31. payments-webhook-ipn
**Funcionalidad**: Endpoint webhook IPN, avanzar estado a CONFIRMADO, decrementar stock
**Historias**: US-046
**Depende de**: payments-mercadopago-integration, orders-state-transitions, products-catalog-crud

---

### 32. frontend-payment-checkout
**Funcionalidad**: CardPayment component, flujo de checkout, visualización de estado
**Historias**: US-045, US-046, US-047, US-048
**Depende de**: payments-mercadopago-integration, frontend-cart-ui, paymentStore

---

## EPIC 08 — PANEL DE ADMINISTRACIÓN

### 33. admin-dashboard-metrics
**Funcionalidad**: KPIs, gráficos con recharts, filtros por fecha
**Historias**: US-052
**Depende de**: orders-creation-fsm, payments-webhook-ipn

---

### 34. admin-users-management
**Funcionalidad**: CRUD usuarios, asignación de roles, soft delete
**Historias**: US-053, US-054
**Depende de**: auth-rbac-roles

---

### 35. admin-stock-management
**Funcionalidad**: Vista de productos con stock bajo, bulk update de stock
**Historias**: US-055
**Depende de**: products-catalog-crud

---

### 36. admin-orders-management
**Funcionalidad**: Vista de todos los pedidos, transiciones de estado, cancelaciones
**Historias**: US-056, US-057, US-058, US-059, US-060
**Depende de**: orders-state-transitions, orders-history-audit-trail

---

### 37. frontend-admin-panel-ui
**Funcionalidad**: Layout del admin, navegación a cada módulo
**Historias**: US-052, US-053, US-054, US-055, US-056, US-057, US-058, US-059, US-060
**Depende de**: admin-dashboard-metrics, admin-users-management, admin-stock-management, admin-orders-management

---

## FASE FINAL

### 38. documentation-api-openapi
**Funcionalidad**: Validar Swagger UI y ReDoc completos
**Historias**: Transversal (CE-08)
**Depende de**: Todos los anteriores

---

### 39. testing-and-polish
**Funcionalidad**: Tests unitarios (pytest), cleanup de código, validación de performance
**Historias**: Bonus +10 pts
**Depende de**: Todos

---

## RESUMEN POR CRITICIDAD

### 🔴 CRÍTICAS (bloqueantes)
| # | Change | Depende de |
|---|--------|-----------|
| 1 | setup-monorepo-base | — |
| 2 | setup-backend-config | 1 |
| 3 | setup-database-seed | 2 |
| 5 | setup-backend-patterns | 3 |
| 6 | setup-zustand-stores | 4 |
| 9 | auth-login-register | 5, 6 |
| 17 | products-catalog-crud | 15, 16, 11 |
| 26 | orders-creation-fsm | 5, 21, 11 |
| 27 | orders-state-transitions | 26, 17 |
| 30 | payments-mercadopago-integration | 26, 6 |
| 31 | payments-webhook-ipn | 30, 27, 17 |
| 32 | frontend-payment-checkout | 30, 25, 6 |

### 🟠 ALTAS
| # | Change | Depende de |
|---|--------|-----------|
| 4 | setup-frontend-config | 1 |
| 7 | setup-error-handling | 2 |
| 8 | setup-rate-limiting | 2 |
| 10 | auth-token-refresh-logout | 9 |
| 11 | auth-rbac-roles | 9 |
| 12 | frontend-auth-guards | 9, 11 |
| 13 | frontend-navigation-ui | 12 |
| 14 | frontend-error-handling | 4 |
| 15 | categories-hierarchical | 5, 11 |
| 16 | ingredients-allergens | 5, 11 |
| 18 | products-associations | 17 |
| 19 | products-public-catalog | 18 |
| 20 | frontend-catalog-ui | 19, 14 |
| 21 | addresses-delivery | 9 |
| 22 | user-profile | 9 |
| 24 | cart-client-side | 6, 18 |
| 25 | frontend-cart-ui | 24, 19 |
| 28 | orders-history-audit-trail | 26 |
| 29 | frontend-orders-list-detail | 27, 28 |
| 33 | admin-dashboard-metrics | 26, 31 |

### 🟡 MEDIAS
| # | Change | Depende de |
|---|--------|-----------|
| 23 | frontend-profile-ui | 21, 22 |
| 34 | admin-users-management | 11 |
| 35 | admin-stock-management | 17 |
| 36 | admin-orders-management | 27, 28 |
| 37 | frontend-admin-panel-ui | 33-36 |

### 🟢 BAJAS
| # | Change | Depende de |
|---|--------|-----------|
| 38 | documentation-api-openapi | Todos |
| 39 | testing-and-polish | Todos |

---

## ORDEN RECOMENDADO DE IMPLEMENTACIÓN

```
Sprint 0 (Infraestructura):  1, 2, 3, 4, 5, 6, 7, 8
Sprint 1 (Auth):             9, 10, 11, 12, 13, 14
Sprint 2 (Catálogo):        15, 16, 17, 18, 19, 20
Sprint 3 (Perfil+Carrito):  21, 22, 23, 24, 25
Sprint 4 (Pedidos):         26, 27, 28, 29
Sprint 5 (Pagos):           30, 31, 32
Sprint 6 (Admin):           33, 34, 35, 36, 37
Sprint 7 (Polish):           38, 39
```

---

**Generado**: 2026-04-28  
**Basado en**: docs/Descripcion.txt, docs/Historias_de_usuario.txt, docs/Integrador.txt  
**Cambios implementados**: 1/39 (solo setup-monorepo-base)