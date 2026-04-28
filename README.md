# 🍔 Food Store — E-Commerce de Alimentos

Sistema integral de e-commerce para gestión de pedidos de comida con React, FastAPI y PostgreSQL.

**Spec-Driven Development (SDD)** · v5.0 · Arquitectura Feature-First

---

## 📋 Requisitos previos

| Herramienta | Versión mínima | Notas |
|-------------|----------------|-------|
| **Python** | 3.10+ | Backend con FastAPI |
| **Node.js** | 18.x+ | Frontend con Vite/React |
| **PostgreSQL** | 15+ | Base de datos relacional |
| **Git** | 2.x+ | Control de versiones |

**Herramientas de desarrollo**:
- Claude Code (AI assistant)
- OpenSpec CLI (`npx @fission-ai/openspec@latest`)

---

## 🚀 Inicio rápido

### 1. Clonar el repositorio

```bash
git clone <url-del-repo> food-store
cd food-store
```

### 2. Setup Backend

```bash
cd backend

# 1. Configurar entorno
cp .env.example .env
# Editar .env con tus credenciales (ver sección Variables de entorno)

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt

# 3. Migrar base de datos
alembic upgrade head

# 4. Cargar datos iniciales (roles, estados, admin)
python -m app.db.seed

# 5. Iniciar servidor
uvicorn app.main:app --reload
```

**Backend disponible**: http://localhost:8000  
**Swagger UI**: http://localhost:8000/docs  
**ReDoc**: http://localhost:8000/redoc

### 3. Setup Frontend

```bash
cd frontend

# 1. Instalar dependencias
npm install

# 2. Configurar entorno
cp .env.example .env.local
# Editar .env.local si es necesario

# 3. Iniciar desarrollo
npm run dev
```

**Frontend disponible**: http://localhost:5173

---

## 📁 Estructura del proyecto

```
food-store/
├── backend/                    # FastAPI + SQLModel + PostgreSQL
│   ├── app/
│   │   ├── core/              # Configuración compartida (config, database, security)
│   │   └── modules/          # M��dulos feature-first (vertical slicing)
│   │       ├── auth/         # Login, registro, refresh, logout
│   │       ├── usuarios/     # CRUD usuarios, roles RBAC
│   │       ├── categorias/   # Categorías jerárquicas con CTE
│   │       ├── productos/    # CRUD productos, ingredientes
│   │       ├── pedidos/      # FSM pedidos, auditoría append-only
│   │       ├── pagos/        # Integración MercadoPago
│   │       ├── direcciones/  # CRUD direcciones de entrega
│   │       ├── admin/        # Dashboard, métricas
│   │       └── refreshtokens/ # Gestión de refresh tokens
│   ├── tests/                # Tests con pytest
│   └── requirements.txt     # Dependencias Python
│
├── frontend/                  # React + TypeScript + Vite
│   ├── src/
│   │   ├── app/             # App root: providers, routing
│   │   ├── pages/           # Rutas/páginas principales
│   │   ├── features/        # Interacciones de usuario (independientes)
│   │   ├── entities/        # Modelos de dominio + hooks básicos
│   │   └── shared/          # Utilidades: api, stores, components
│   └── package.json
│
├── docs/                      # Documentación técnica
│   ├── Descripcion.txt       # Visión general, actores, stack
│   ├── Integrador.txt        # Arquitectura, ERD v5, API REST
│   └── Historias_de_usario.txt  # US-000 a US-076
│
└── openspec/                  # Artefactos SDD (generados por CLI)
    ├── changes/              # Changes propuestos e implementados
    └── specs/                # Especificaciones archivadas
```

### Arquitectura Backend — Capas

```
Router → Service → Unit of Work → Repository → Model
```

- **Router**: HTTP puro (validación de schemas)
- **Service**: Lógica de negocio (stateless)
- **Unit of Work**: Transacciones atómicas
- **Repository**: Acceso a datos
- **Model**: Entidades SQLModel

### Arquitectura Frontend — FSD

```
Pages → Features → Entities → Shared
```

- **app**: Providers globales, routing
- **pages**: Rutas completas
- **features**: Interacciones de usuario autocontenidas
- **entities**: Modelos de dominio + hooks de datos
- **shared**: Componentes/utilidades reutilizables

---

## 📚 Documentación

| Archivo | Contenido |
|---------|-----------|
| [`docs/Descripcion.txt`](docs/Descripcion.txt) | Visión general, actores, stack tecnológico |
| [`docs/Integrador.txt`](docs/Integrador.txt) | Arquitectura en capas, ERD v5, API REST |
| [`docs/Historias_de_usuario.txt`](docs/Historias_de_usuario.txt) | US-000 a US-076 completas |
| [`backend/README.md`](backend/README.md) | Setup detallado backend |
| [`frontend/README.md`](frontend/README.md) | Setup detallado frontend |

---

## 🛠️ Stack tecnológico

| Aspecto | Tecnología | Versión |
|---------|------------|---------|
| Backend | FastAPI | 0.111+ |
| ORM | SQLModel | 0.0.19+ |
| Database | PostgreSQL | 15+ |
| Migrations | Alembic | 1.13+ |
| Auth | JWT (python-jose) + bcrypt | — |
| Rate Limiting | slowapi | 0.1.9+ |
| Payments | MercadoPago SDK | 2.3.0+ |
| Frontend | React + TypeScript | 18.x + 5.x |
| Build | Vite | 5.x |
| Styles | Tailwind CSS | 3.x |
| Server State | TanStack Query | 5.x |
| Forms | TanStack Form | 0.x |
| Client State | Zustand | 4.x |
| HTTP Client | Axios | 1.x |
| Charts | Recharts | 2.x |

---

## 🔐 Roles y permisos (RBAC)

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **ADMIN** | Administrador | CRUD completo, métricas, configuración |
| **STOCK** | Gestor de Stock | Catálogo, productos, stock, ingredientes |
| **PEDIDOS** | Gestor de Pedidos | Ver y avanzar pedidos, historial |
| **CLIENT** | Cliente | Ver catálogo, carrito, mis pedidos |

---

## 🤝 Contribuir

1. **Clonar y explorar**: `git clone <url> && cd food-store`
2. **Crear branch**: `git checkout -b feat/nombre-descriptivo`
3. **Commits pequeños**: Conventional commits (`feat:`, `fix:`, `chore:`, `docs:`)
4. **Abrir PR**: Describir qué, por qué y cómo
5. **Code review**: Arquitectura, tests, convenciones, seguridad

### Convenciones de commits

```
feat(auth): add login with JWT refresh
fix(orders): prevent negative stock on cancel
docs(categories): update CTE recursion example
chore: add pytest fixtures for orders
test(payments): mock MercadoPago webhook response
```

---

## 📖 Flujo de desarrollo con OPSX

```
/opsx:explore   →  Pensar y analizar antes de implementar
/opsx:propose   →  Generar propuesta + diseño + tasks
/opsx:apply     →  Implementar tarea por tarea
/opsx:archive   →  Sincronizar specs y cerrar change
```

Ver [docs/CHANGES.md](docs/CHANGES.md) para guía completa.

---

## 📝 Licencia

MIT License — ver archivo [`LICENSE`](LICENSE)

---

## 📞 Contacto

- Issues: https://github.com/tu-usuario/food-store/issues
- Discussions: https://github.com/tu-usuario/food-store/discussions

---

**Spec-Driven Development (SDD)** · Food Store v5.0  
Última actualización: 2026-04-28