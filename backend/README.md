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

## Estructura

```
backend/
├── app/
│   ├── main.py              # FastAPI entry point
│   ├── api/                 # Routers HTTP (10 thin routers)
│   ├── core/               # Configuracion centralizada
│   │   ├── uow.py          # Unit of Work (commit/rollback automatico)
│   │   ├── repositories/   # BaseRepository[T] generico
│   │   ├── config.py       # Environment variables (pydantic-settings)
│   │   ├── database.py     # SQLAlchemy session + engine
│   │   └── security.py     # JWT, bcrypt utilities
│   ├── domain/             # Modulos feature-first (vertical slicing)
│   │   ├── auth/          # service, repository, schemas
│   │   ├── usuarios/      # service, repository, schemas
│   │   ├── categorias/    # service, repository, schemas
│   │   ├── productos/     # service, repository, schemas
│   │   ├── pedidos/       # service, repository, schemas
│   │   ├── pagos/         # service, repository, schemas
│   │   ├── direcciones/   # service, repository, schemas
│   │   └── admin/         # service, schemas
│   ├── models/            # Modelos SQLModel (centralizados, 16 tablas)
│   └── db/                # Seed data (idempotente)
├── tests/                  # 254 tests con pytest
├── Makefile               # Comandos make (test, test-cov, dev)
├── requirements.txt       # Dependencias Python
├── alembic.ini           # Alembic configuration
└── .env.example         # Environment variables template
```

### Arquitectura - Capas

```
Router (HTTP) -> Service (logica) -> Unit of Work (transaccion) -> Repository (datos) -> Model (SQLModel)
```

- **Router**: HTTP puro, valida schemas, delega al Service. Sin logica de negocio.
- **Service**: Logica de negocio stateless, orquesta via UoW. Lanza HTTPException.
- **Unit of Work**: Gestiona transaccion, commit/rollback automatico. Ningun service hace session.commit() directo.
- **Repository**: Acceso a BD, hereda de BaseRepository[T] generico.
- **Model**: Entidades SQLModel con relaciones. Sin imports de capas superiores.

Los modulos de dominio contienen: `service.py`, `repository.py` (si tiene queries especificas), `schemas.py`.
Los modelos estan centralizados en `app/models/` para mantener la metadata de SQLAlchemy consistente.

---

## Comandos

| Comando | Descripcion |
|---------|------------|
| `uvicorn app.main:app --reload` | Desarrollo en http://localhost:8000 |
| `alembic upgrade head` | Aplicar migraciones |
| `alembic revision --autogenerate -m "message"` | Generar migracion |
| `alembic downgrade -1` | Revertir ultima migracion |
| `python -m app.db.seed` | Cargar datos iniciales (idempotente) |
| `pytest` | Ejecutar 254 tests |
| `pytest --cov=app --cov-report=html` | Tests con cobertura |
| `make test` | Tests via Makefile |
| `make test-cov-html` | Tests + reporte HTML |

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

## Testing

```bash
# Activar entorno
source .venv/bin/activate

# Ejecutar tests (254 tests)
pytest

# Coverage (84% actual)
pytest --cov=app --cov-report=html
# Abrir htmlcov/index.html en el navegador

# Coverage rapido
pytest --cov=app --cov-report=term-missing

# Via Makefile
make test
make test-cov
make test-cov-html
```

---

## 📚 Convenciones de código

- **Archivos**: `snake_case.py`
- **Funciones/variables**: `snake_case`
- **Clases**: `PascalCase`
- **Imports**: absolutos desde `app.domain.<modulo>` (service, repository, schemas)
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