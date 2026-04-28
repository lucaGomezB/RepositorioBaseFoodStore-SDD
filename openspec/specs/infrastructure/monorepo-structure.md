# Monorepo Structure Specification

## Overview

| Aspect | Value |
|--------|-------|
| **Capability** | infrastructure |
| **Change** | setup-monorepo-base |
| **Status** | implemented |
| **Archived** | 2026-04-28 |
| **Commit** | 899f10f |

## Purpose

Defines the base directory structure for the Food Store monorepo, separating backend (FastAPI) and frontend (React) with their respective architectural patterns.

## Architecture

### Backend — Feature-First

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── core/                  # Shared configuration
│   │   ├── __init__.py
│   │   ├── config.py          # Environment variables
│   │   ├── database.py       # SQLAlchemy session
│   │   └── security.py      # JWT, bcrypt
│   └── modules/               # Feature-first modules
│       ├── __init__.py
│       ├── auth/             # Login, register, refresh, logout
│       ├── usuarios/         # CRUD users, RBAC
│       ├── categorias/       # Hierarchical categories
│       ├── productos/       # CRUD products, ingredients
│       ├── pedidos/         # FSM orders, audit trail
│       ├── pagos/           # MercadoPago integration
│       ├── direcciones/     # Delivery addresses
│       ├── admin/          # Dashboard, metrics
│       └── refreshtokens/  # Refresh token management
├── tests/
│   ├── __init__.py
│   └── conftest.py         # pytest fixtures
├── requirements.txt
├── .env.example
└── README.md
```

**Layer flow**: `Router → Service → Unit of Work → Repository → Model`

### Frontend — Feature-Sliced Design

```
frontend/
├── src/
│   ├── app/                  # App root
│   │   ├── App.tsx
│   │   ├── router.tsx
│   │   └── app.css
│   ├── pages/                # Route pages
│   ├── features/            # User interactions
│   │   ├── auth/
│   │   ├── catalog/
│   │   ├── cart/
│   │   ├── orders/
│   │   ├── payments/
│   │   └── admin/
│   ├── entities/            # Domain models
│   │   ├── user/
│   │   ├── product/
│   │   ├── order/
│   │   └── address/
│   └── shared/             # Utilities
│       ├── api/
│       ├── stores/
│       ├── components/
│       ├── hooks/
│       ├── types/
│       ├── utils/
│       └── styles/
├── public/
├── .env.example
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── index.html
```

**Layer flow**: `Pages → Features → Entities → Shared`

## Requirements

### Backend

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| PostgreSQL | 15+ |

### Frontend

| Requirement | Version |
|-------------|---------|
| Node.js | 18.x+ |
| npm | 9.x+ |

## Files Created

### Root

- `.gitignore` — Excludes .env, __pycache__, node_modules, .venv, dist, .DS_Store
- `.gitattributes` — Line ending normalization
- `README.md` — Project overview and setup
- `LICENSE` — MIT License
- `CONTRIBUTING.md` — Contribution guidelines

### Backend (19 files)

- `backend/app/__init__.py`
- `backend/app/main.py`
- `backend/app/core/__init__.py`
- `backend/app/core/config.py`
- `backend/app/core/database.py`
- `backend/app/core/security.py`
- `backend/app/modules/__init__.py`
- `backend/app/modules/auth/__init__.py`
- `backend/app/modules/usuarios/__init__.py`
- `backend/app/modules/categorias/__init__.py`
- `backend/app/modules/productos/__init__.py`
- `backend/app/modules/pedidos/__init__.py`
- `backend/app/modules/pagos/__init__.py`
- `backend/app/modules/direcciones/__init__.py`
- `backend/app/modules/admin/__init__.py`
- `backend/app/modules/refreshtokens/__init__.py`
- `backend/tests/__init__.py`
- `backend/tests/conftest.py`
- `backend/requirements.txt`
- `backend/.env.example`

### Frontend (20 files)

- `frontend/src/app/App.tsx`
- `frontend/src/app/router.tsx`
- `frontend/src/app/app.css`
- `frontend/src/index.tsx`
- `frontend/src/entities/user/index.ts`
- `frontend/src/entities/product/index.ts`
- `frontend/src/entities/order/index.ts`
- `frontend/src/entities/address/index.ts`
- `frontend/src/shared/api/client.ts`
- `frontend/src/shared/stores/index.ts`
- `frontend/src/shared/types/index.ts`
- `frontend/src/shared/types/api.ts`
- `frontend/src/shared/utils/index.ts`
- `frontend/vite.config.ts`
- `frontend/tailwind.config.js`
- `frontend/postcss.config.js`
- `frontend/index.html`
- `frontend/public/favicon.ico`
- `frontend/tsconfig.json`
- `frontend/package.json`
- `frontend/.env.example`

## Environment Variables

### Backend (.env.example)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/foodstore_db
SECRET_KEY=your-super-secret-key-min-32-chars-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
CORS_ORIGINS=http://localhost:5173
MERCADOPAGO_ACCESS_TOKEN=TEST-your-access-token-here
MERCADOPAGO_PUBLIC_KEY=TEST-your-public-key-here
MERCADOPAGO_WEBHOOK_SECRET=your-webhook-secret
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### Frontend (.env.example)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_MERCADOPAGO_PUBLIC_KEY=TEST-your-public-key-here
VITE_ENV=development
```

## Conventions

### Backend

- Files: `snake_case.py`
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Imports: absolute from `app.modules`

### Frontend

- Components: `PascalCase.tsx`
- Utilities: `camelCase.ts`
- TanStack Query keys: `['entity', params]`

## Dependencies with Other Specs

This spec is the **foundation** — all other infrastructure specs depend on it:

- `setup-backend-config` depends on `monorepo-structure`
- `setup-database-seed` depends on `monorepo-structure`
- `setup-frontend-config` depends on `monorepo-structure`

## Notes

- This is a **foundation spec** — no business capability, just infrastructure
- All modules are empty placeholders (comments only)
- No actual code — structure only
- Commits are progressive: 7 commits (not a "big bang")