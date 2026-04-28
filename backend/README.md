# 🍔 Food Store — Backend

FastAPI + SQLModel + PostgreSQL para sistema de e-commerce de alimentos.

---

## ⚡ Inicio rápido

```bash
# 1. Configurar entorno
cp .env.example .env
# Editar .env con tus credenciales

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate      # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Migrar base de datos
alembic upgrade head

# 5. Cargar datos iniciales (roles, estadospedido, admin)
python -m app.db.seed

# 6. Iniciar servidor
uvicorn app.main:app --reload
```

**API**: http://localhost:8000  
**Swagger UI**: http://localhost:8000/docs  
**ReDoc**: http://localhost:8000/redoc

---

## 📁 Estructura

```
backend/
├── app/
│   ├── __init__.py           # FastAPI app initialization
│   ├── main.py              # FastAPI entry point
│   ├── core/               # Configuración centralizada
│   │   ├── config.py       # Environment variables (pydantic-settings)
│   │   ├── database.py    # SQLAlchemy session + engine
│   │   └── security.py   # JWT, bcrypt utilities
│   ├── modules/           # Feature-first modules
│   │   ├── auth/         # Login, register, refresh, logout
│   │   ├── usuarios/     # CRUD usuarios, RBAC
│   │   ├── categorias/   # Categorías jerárquicas (CTE)
│   │   ├── productos/    # CRUD productos, ingredientes
│   │   ├── pedidos/     # FSM pedidos, audit trail
│   │   ├── pagos/       # MercadoPago integration
│   │   ├── direcciones/ # CRUD direcciones entrega
│   │   ├── admin/       # Dashboard, métricas
│   │   └── refreshtokens/ # Refresh token management
│   └── tests/            # Tests con pytest
├── requirements.txt       # Dependencias Python
├── alembic.ini           # Alembic configuration
└── .env.example         # Environment variables template
```

### Arquitectura — Capas

```
Router (HTTP) → Service (lógica) → Unit of Work (transacción) → Repository (datos) → Model (SQLModel)
```

Cada módulo tiene su propia carpeta con:
- `model.py` — Entidad SQLModel
- `schemas.py` — Pydantic schemas (Create, Update, Read)
- `repository.py` — Acceso a datos
- `service.py` — Lógica de negocio
- `router.py` — Endpoints HTTP

---

## 🔧 Comandos

| Comando | Descripción |
|---------|-----------|
| `uvicorn app.main:app --reload` | Desarrollo en http://localhost:8000 |
| `alembic upgrade head` | Aplicar migraciones |
| `alembic revision --autogenerate -m "message"` | Generar migración |
| `alembic downgrade -1` | Revertir última migración |
| `python -m app.db.seed` | Cargar datos iniciales |
| `pytest` | Ejecutar tests |

---

## 🔐 Variables de entorno

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/foodstore_db

# Security - JWT
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:5173

# MercadoPago
MERCADOPAGO_ACCESS_TOKEN=TEST-xxx
MERCADOPAGO_PUBLIC_KEY=TEST-xxx
```

---

## 🧪 Testing

```bash
# Activar entorno
source .venv/bin/activate

# Ejecutar tests
pytest

# Coverage
pytest --cov=app --cov-report=html
```

---

## 📚 Convenciones de código

- **Archivos**: `snake_case.py`
- **Funciones/variables**: `snake_case`
- **Clases**: `PascalCase`
- **Imports**: absolutos desde `app.modules`
- **Schemas Pydantic**: `{Entidad}{Tipo}` (ej: `UserCreate`, `UserRead`)
- **HTTP Methods**: GET (lectura), POST (crear), PUT (reemplazar), PATCH (actualizar), DELETE (borrar)

---

## 📖 Documentación relacionada

- [README raíz](../README.md) — Setup general
- [docs/Integrador.txt](../docs/Integrador.txt) — Arquitectura completa
- [docs/Historias_de_usuario.txt](../docs/Historias_de_usuario.txt) — Historias de usuario

---

**Stack**: FastAPI · SQLModel · PostgreSQL · Alembic · JWT  
**Mantenido por**: Food Store Contributors