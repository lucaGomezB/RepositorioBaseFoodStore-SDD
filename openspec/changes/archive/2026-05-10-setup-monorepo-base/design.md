# Design: setup-monorepo-base

## Arquitectura de alto nivel

```
RepositorioBaseFoodStore-SDD/
├── .git/                           ← Inicializado con commits progresivos
├── .gitignore                      ← Exclusiones de build, deps, env, OS
├── README.md                       ← Documentación raíz
├── LICENSE                         ← MIT o similar
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 ← Placeholder (FastAPI app entry point)
│   │   ├── core/                   ← Configuración centralizada
│   │   │   ├── __init__.py
│   │   │   ├── config.py           ← Placeholder (env vars)
│   │   │   ├── database.py         ← Placeholder (SQLAlchemy session)
│   │   │   └── security.py         ← Placeholder (JWT, bcrypt)
│   │   └── modules/                ← Feature-first: cada módulo independiente
│   │       ├── __init__.py
│   │       ├── auth/               ← Será: login, register, refresh, logout
│   │       ├── usuarios/           ← Será: CRUD usuarios, roles
│   │       ├── categorias/         ← Será: categorías jerárquicas
│   │       ├── productos/          ← Será: CRUD productos, ingredientes
│   │       ├── pedidos/            ← Será: FSM pedidos, creación, historial
│   │       ├── pagos/              ← Será: MercadoPago integration
│   │       ├── direcciones/        ← Será: CRUD direcciones entrega
│   │       ├── admin/              ← Será: dashboard, métricas, bulk ops
│   │       └── refreshtokens/      ← Será: gestión de refresh tokens
│   ├── tests/
│   │   ├── __init__.py
│   │   └── conftest.py             ← Placeholder (pytest fixtures)
│   ├── requirements.txt            ← Placeholder (dependencias Python)
│   ├── .env.example                ← Variables de entorno documentadas
│   └── README.md                   ← Setup backend específico
│
├── frontend/
│   ├── src/
│   │   ├── app/                    ← App root: providers, theme, routing
│   │   │   ├── App.tsx
│   │   │   ├── app.css
│   │   │   └── router.tsx          ← React Router DOM config
│   │   ├── pages/                  ← Rutas/páginas principales
│   │   │   ├── HomePage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── NotFoundPage.tsx
│   │   │   └── ...
│   │   ├── features/               ← Interacciones de usuario (independientes)
│   │   │   ├── auth/               ← Será: LoginForm, RegisterForm
│   │   │   ├── catalog/            ← Será: ProductGrid, FilterBar
│   │   │   ├── cart/               ← Será: CartDrawer, AddToCart
│   │   │   ├── orders/             ← Será: OrdersList, OrderDetail
│   │   │   ├── payments/           ← Será: CardPayment, CheckoutFlow
│   │   │   └── admin/              ← Será: Dashboard, CRUDs
│   │   ├── entities/               ← Modelos de dominio + hooks básicos
│   │   │   ├── user/               ← Será: User type, useUser hook
│   │   │   ├── product/            ← Será: Product type, useProducts hook
│   │   │   ├── order/              ← Será: Order type, useOrders hook
│   │   │   └── ...
│   │   ├── shared/                 ← Utilidades compartidas
│   │   │   ├── api/                ← Será: axios instance, interceptors
│   │   │   │   └── client.ts
│   │   │   ├── stores/             ← Será: Zustand stores (auth, cart, payment, ui)
│   │   │   ├── components/         ← Componentes UI genéricos
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── ...
│   │   │   ├── hooks/              ← Custom hooks compartidos
│   │   │   │   └── useDebounce.ts
│   │   │   ├── types/              ← Tipos globales
│   │   │   │   ├── index.ts
│   │   │   │   └── api.ts
│   │   │   ├── utils/              ← Funciones utilitarias
│   │   │   │   ├── formatters.ts
│   │   │   │   └── validators.ts
│   │   │   └── styles/             ← Estilos globales
│   │   │       └── globals.css
│   │   └── index.tsx               ← Entrada: ReactDOM.createRoot(App)
│   ├── public/
│   │   ├── favicon.ico
│   │   └── ...
│   ├── .env.example                ← Variables de entorno (Vite: VITE_*)
│   ├── package.json                ← Placeholder (npm scripts, dependencies)
│   ├── tsconfig.json               ← Placeholder (TypeScript config: strict: true)
│   ├── vite.config.ts              ← Placeholder (Vite + React + SWC)
│   ├── tailwind.config.js          ← Placeholder (Tailwind CSS)
│   ├── postcss.config.js           ← Placeholder (PostCSS para Tailwind)
│   ├── index.html                  ← Raíz HTML (root div)
│   └── README.md                   ← Setup frontend específico
│
└── docs/                           ← (Ya existe) Especificación técnica

```

## Archivos específicos a crear

### `.gitignore` (en raíz)

```
# Backend
backend/.env
backend/.venv/
backend/venv/
backend/__pycache__/
backend/*.pyc
backend/*.pyo
backend/*.egg-info/
backend/dist/
backend/build/
backend/.pytest_cache/
backend/.coverage

# Frontend
frontend/node_modules/
frontend/.env.local
frontend/.env.*.local
frontend/dist/
frontend/build/
frontend/.DS_Store
frontend/*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*.sublime-*

# OS
.DS_Store
Thumbs.db
*.tmp

# Local development
.env
.env.local
```

### `README.md` (en raíz)

```markdown
# 🍔 Food Store — E-Commerce de Alimentos

Sistema integral de e-commerce para gestión de pedidos de comida con React, FastAPI y PostgreSQL.

## 📋 Requisitos previos

- **Node.js**: 18.x o superior (para frontend)
- **Python**: 3.10 o superior (para backend)
- **PostgreSQL**: 15 o superior (para datos)
- **Git**: 2.x o superior

## 🚀 Inicio rápido

### 1. Clonar el repositorio

\`\`\`bash
git clone https://github.com/tu-usuario/RepositorioBaseFoodStore-SDD.git
cd RepositorioBaseFoodStore-SDD
\`\`\`

### 2. Setup Backend

\`\`\`bash
cd backend
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus variables (DATABASE_URL, SECRET_KEY, etc.)
alembic upgrade head
python -m app.db.seed
uvicorn app.main:app --reload
\`\`\`

Backend disponible en: **http://localhost:8000**  
Swagger UI: **http://localhost:8000/docs**

### 3. Setup Frontend

\`\`\`bash
cd frontend
npm install
cp .env.example .env.local
# Editar .env.local si es necesario
npm run dev
\`\`\`

Frontend disponible en: **http://localhost:5173**

## 📁 Estructura del proyecto

- **`/backend`**: FastAPI + SQLModel + PostgreSQL
  - Arquitectura en capas: Router → Service → UoW → Repository → Model
  - Módulos feature-first (vertical slicing)
  
- **`/frontend`**: React + TypeScript + Vite
  - Feature-Sliced Design (FSD)
  - Zustand para estado global
  - TanStack Query para datos del servidor
  
- **`/docs`**: Especificación técnica completa (Descripcion.txt, Historias_de_usuario.txt, etc.)

## 📚 Documentación

- [Especificación técnica](./docs/Descripcion.txt)
- [Historias de usuario](./docs/Historias_de_usuario.txt)
- [Setup detallado backend](./backend/README.md)
- [Setup detallado frontend](./frontend/README.md)

## 🛠️ Stack tecnológico

| Aspecto | Tecnología |
|--------|-----------|
| Backend | FastAPI, SQLModel, PostgreSQL, Alembic |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Autenticación | JWT (access + refresh tokens), bcrypt |
| Pagos | MercadoPago SDK |
| Gestión de estado | Zustand (cliente), TanStack Query (servidor) |

## 📖 Convenciones de código

- **Backend**: `snake_case` para funciones/variables, `PascalCase` para clases
- **Frontend**: `camelCase` para funciones/variables, `PascalCase` para componentes
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/)
- **Python**: PEP 8 con pre-commit hooks
- **TypeScript**: `strict: true`, sin `any`

## 🤝 Colaboración

1. Crea un branch desde `main`: `git checkout -b feat/descripcion-corta`
2. Haz commits pequeños y descriptivos
3. Sube el branch y abre un PR
4. La revisión cubre: arquitectura, tests, convenciones, seguridad

## 📝 Licencia

MIT

## 📞 Contacto

- [Issues](https://github.com/tu-usuario/RepositorioBaseFoodStore-SDD/issues)
- [Discussions](https://github.com/tu-usuario/RepositorioBaseFoodStore-SDD/discussions)

---

**Spec-Driven Development (SDD)** · Food Store v5.0  
Última actualización: 2026-04-28
```

### `.env.example` (Backend)

```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/foodstore_db

# Security
SECRET_KEY=your-super-secret-key-min-32-chars-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:5173"]

# MercadoPago
MERCADOPAGO_ACCESS_TOKEN=TEST-your-access-token-here
MERCADOPAGO_PUBLIC_KEY=TEST-your-public-key-here
MERCADOPAGO_WEBHOOK_SECRET=your-webhook-secret

# Logging
LOG_LEVEL=INFO

# Environment
ENVIRONMENT=development
```

### `.env.example` (Frontend)

```
# API Backend
VITE_API_BASE_URL=http://localhost:8000/api/v1

# MercadoPago
VITE_MERCADOPAGO_PUBLIC_KEY=TEST-your-public-key-here

# Environment
VITE_ENV=development
```

## Decisiones de diseño

1. **Monorepo vs. Polyrepo**: Monorepo (un solo repo, carpetas separadas) para simplificar el setup y la colaboración
2. **Feature-first backend**: Cada módulo contiene su router, service, repository, model. Claridad máxima.
3. **FSD Frontend**: Separación clara por capas (app, pages, features, entities, shared). Evita "component hell".
4. **Convenciones de naming**: Backend snake_case, Frontend camelCase. Respeta normas de cada ecosistema.
5. **Git limpio**: Commits pequeños y descriptivos desde el inicio. Facilita rebase y cherry-pick.

## Riesgos y mitigación

| Riesgo | Mitigación |
|--------|-----------|
| Estructura no respetada por equipo futuro | Documentación clara en README + ejemplos comentados |
| Imports circulares en frontend FSD | Convención: solo importar de capas inferiores |
| .gitignore incompleto | Usar template probado + agregar durante desarrollo |

## Entregables

- ✅ Estructura de carpetas creada
- ✅ Archivos placeholder vacíos en lugar correcto
- ✅ .gitignore configurado
- ✅ README.md con instrucciones completas
- ✅ .env.example en ambas capas
- ✅ Commits progresivos documentados
