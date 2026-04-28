# Tasks: setup-monorepo-base

## Checklist de implementación atómica

Cada tarea representa un commit + un paso completable en máximo 30 minutos.

---

### ✅ TASK 1: Inicializar Git y crear .gitignore

**Descripción**: Crear repositorio Git inicializado y agregar .gitignore completo

**Pasos**:
1. Desde la raíz del proyecto, ejecutar: `git init`
2. Crear archivo `.gitignore` en la raíz con contenido completo (ver design.md)
3. Agregar a staging: `git add .gitignore`
4. Hacer commit: `git commit -m "chore: initialize .gitignore for monorepo"`

**Verificación**:
- `git log` muestra el commit
- `cat .gitignore` muestra exclusiones para `.env`, `__pycache__`, `node_modules`, `.venv`, `dist`, `.DS_Store`
- `git status` está limpio

**Tiempo estimado**: 10 min

---

### ✅ TASK 2: Crear estructura de carpetas Backend

**Descripción**: Crear todas las carpetas y archivos placeholder para el backend con estructura feature-first

**Pasos**:
1. Crear directorios:
   ```
   backend/
   ├── app/
   │   ├── core/
   │   ├── modules/
   │   │   ├── auth/
   │   │   ├── usuarios/
   │   │   ├── categorias/
   │   │   ├── productos/
   │   │   ├── pedidos/
   │   │   ├── pagos/
   │   │   ├── direcciones/
   │   │   ├── admin/
   │   │   └── refreshtokens/
   │   └── tests/
   ```

2. Crear archivos `__init__.py` en cada directorio vacío (necesario para que Python reconozca packages)

3. Crear placeholders:
   - `backend/app/main.py` (vacío con comentario: "# FastAPI app entry point")
   - `backend/app/core/config.py` (vacío con comentario)
   - `backend/app/core/database.py` (vacío con comentario)
   - `backend/app/core/security.py` (vacío con comentario)
   - `backend/tests/conftest.py` (vacío con comentario: "# pytest fixtures")
   - `backend/requirements.txt` (vacío con comentario: "# Python dependencies")

4. Agregar a staging: `git add backend/`

5. Commit: `git commit -m "chore: scaffold backend directory structure (feature-first)"`

**Verificación**:
- `ls -R backend/` muestra todas las carpetas
- Todos los `__init__.py` existen
- `git status` no muestra errores

**Tiempo estimado**: 15 min

---

### ✅ TASK 3: Crear estructura de carpetas Frontend

**Descripción**: Crear todas las carpetas y archivos placeholder para el frontend con FSD

**Pasos**:
1. Crear directorios:
   ```
   frontend/
   ├── src/
   │   ├── app/
   │   ├── pages/
   │   ├── features/
   │   │   ├── auth/
   │   │   ├── catalog/
   │   │   ├── cart/
   │   │   ├── orders/
   │   │   ├── payments/
   │   │   └── admin/
   │   ├── entities/
   │   │   ├── user/
   │   │   ├── product/
   │   │   ├── order/
   │   │   └── address/
   │   ├── shared/
   │   │   ├── api/
   │   │   ├── stores/
   │   │   ├── components/
   │   │   ├── hooks/
   │   │   ├── types/
   │   │   ├── utils/
   │   │   └── styles/
   │   └── index.tsx
   ├── public/
   └── ...
   ```

2. Crear archivos placeholder (con comentarios):
   - `frontend/src/app/App.tsx`
   - `frontend/src/app/router.tsx`
   - `frontend/src/app/app.css`
   - `frontend/src/index.tsx`
   - `frontend/public/favicon.ico` (vacío o placeholder)
   - `frontend/index.html` (minimal con `<div id="root"></div>`)

3. Agregar a staging: `git add frontend/`

4. Commit: `git commit -m "chore: scaffold frontend directory structure (feature-sliced design)"`

**Verificación**:
- `ls -R frontend/src/` muestra todas las capas (app, pages, features, entities, shared)
- `git status` sin errores

**Tiempo estimado**: 15 min

---

### ✅ TASK 4: Crear .env.example en ambas capas

**Descripción**: Crear archivos `.env.example` con variables documentadas

**Pasos**:
1. Crear `backend/.env.example` con contenido (ver design.md):
   - DATABASE_URL
   - SECRET_KEY
   - ALGORITHM
   - ACCESS_TOKEN_EXPIRE_MINUTES
   - REFRESH_TOKEN_EXPIRE_DAYS
   - CORS_ORIGINS
   - MERCADOPAGO_*
   - LOG_LEVEL
   - ENVIRONMENT

2. Crear `frontend/.env.example` con contenido:
   - VITE_API_BASE_URL
   - VITE_MERCADOPAGO_PUBLIC_KEY
   - VITE_ENV

3. Agregar a staging: `git add backend/.env.example frontend/.env.example`

4. Commit: `git commit -m "chore: add environment variable templates"`

**Verificación**:
- `cat backend/.env.example` muestra todas las variables documentadas
- `cat frontend/.env.example` muestra variables Vite
- Ambos archivos son legibles y tienen comentarios explicativos

**Tiempo estimado**: 10 min

---

### ✅ TASK 5: Crear README.md raíz

**Descripción**: Crear documentación principal del proyecto

**Pasos**:
1. Crear `README.md` en la raíz con contenido completo (ver design.md):
   - Titulo y descripción
   - Requisitos previos (Node, Python, PostgreSQL, Git)
   - Instrucciones de setup (backend, frontend)
   - URLs de acceso local
   - Estructura del proyecto
   - Links a documentación específica
   - Stack tecnológico
   - Convenciones de código
   - Licencia

2. Agregar a staging: `git add README.md`

3. Commit: `git commit -m "docs: add root README with setup instructions"`

**Verificación**:
- `cat README.md | head -20` muestra título y descripción
- Contiene instrucciones paso a paso
- URLs y puertos son correctos (backend 8000, frontend 5173)
- Markdown está bien formateado

**Tiempo estimado**: 15 min

---

### ✅ TASK 6: Crear README.md específicos (Backend y Frontend)

**Descripción**: Crear documentación detallada por capa

**Pasos**:
1. Crear `backend/README.md` con:
   - Descripción del backend
   - Setup: venv, pip install, env vars
   - Comandos: `alembic upgrade head`, `python -m app.db.seed`, `uvicorn app.main:app --reload`
   - URLs: Swagger UI en /docs, ReDoc en /redoc
   - Estructura de módulos (feature-first)
   - Convenciones: snake_case, PEP 8

2. Crear `frontend/README.md` con:
   - Descripción del frontend
   - Setup: npm install, env vars
   - Comandos: `npm run dev` (desarrollo), `npm run build` (producción)
   - URLs: http://localhost:5173
   - Estructura: FSD (app, pages, features, entities, shared)
   - Convenciones: camelCase, PascalCase para componentes, TypeScript strict

3. Agregar a staging: `git add backend/README.md frontend/README.md`

4. Commit: `git commit -m "docs: add backend and frontend README files"`

**Verificación**:
- Ambos README contienen instrucciones claras
- Commands son ejecutables
- Estructura y convenciones están documentadas

**Tiempo estimado**: 15 min

---

### ✅ TASK 7: Crear Licencia y archivos finales

**Descripción**: Completar documentación y configuración final

**Pasos**:
1. Crear `LICENSE` (MIT o Apache 2.0):
   ```
   MIT License
   
   Copyright (c) 2026 Food Store Contributors
   
   Permission is hereby granted, free of charge, to any person obtaining a copy...
   [Contenido completo de MIT License]
   ```

2. Crear `CONTRIBUTING.md` (opcional pero recomendado):
   - Cómo contribuir
   - Convenciones de commits
   - Cómo abrir PRs

3. Crear `.gitattributes` (opcional):
   ```
   * text=auto
   *.py text eol=lf
   *.js text eol=lf
   *.ts text eol=lf
   *.json text eol=lf
   ```

4. Agregar a staging: `git add LICENSE CONTRIBUTING.md .gitattributes`

5. Commit: `git commit -m "docs: add license and contributing guidelines"`

**Verificación**:
- `cat LICENSE` muestra licencia completa
- CONTRIBUTING.md es legible

**Tiempo estimado**: 10 min

---

### ✅ TASK 8: Verificar estructura final y documentación

**Descripción**: Validación final de toda la estructura

**Pasos**:
1. Ejecutar `git log --oneline`:
   - Debe mostrar entre 5-8 commits progresivos
   - Cada commit debe ser descriptivo (chore, docs, etc.)

2. Ejecutar `git status`:
   - Debe estar limpio (no untracked files)

3. Validar estructura:
   - `ls -R backend/` muestra estructura completa
   - `ls -R frontend/src/` muestra FSD con todas las capas
   - `.gitignore` está en raíz
   - README.md está en raíz, backend/ y frontend/

4. Validar documentación:
   - README.md raíz tiene instrucciones claras
   - .env.example tiene variables documentadas
   - Cada README específico es completo

5. Ejecutar (en máquina limpia):
   - `git clone . test-clone` (clonar en directorio temporal)
   - Explorar estructura: `ls -R test-clone/`
   - Verificar que se puede leer sin errores
   - Limpiar: `rm -rf test-clone`

**Verificación checklist**:
- ✅ .gitignore excluye .env, __pycache__, node_modules, .venv, dist, .DS_Store
- ✅ README.md raíz contiene: descripción, prerequisites, setup (backend + frontend), estructura, stack, convenciones
- ✅ backend/.env.example documentado
- ✅ frontend/.env.example documentado
- ✅ backend/ estructura completa con __init__.py en todos lados
- ✅ frontend/src/ tiene app/, pages/, features/, entities/, shared/
- ✅ Entre 5-8 commits con mensajes claros
- ✅ No hay archivos sin seguimiento (git status clean)
- ✅ Se puede clonar y explorar sin errores

**Tiempo estimado**: 20 min

---

## Resumen de commits esperados

```
chore: initialize .gitignore for monorepo
chore: scaffold backend directory structure (feature-first)
chore: scaffold frontend directory structure (feature-sliced design)
chore: add environment variable templates
docs: add root README with setup instructions
docs: add backend and frontend README files
docs: add license and contributing guidelines
docs: final validation of monorepo structure
```

## Criterios de aceptación final

- ✅ Repositorio inicializado con Git
- ✅ Estructura backend y frontend claramente separadas
- ✅ .gitignore correctamente excluye artefactos de build
- ✅ README.md raíz con instrucciones completas
- ✅ .env.example en ambas capas
- ✅ 6-8 commits progresivos con mensajes descriptivos
- ✅ Se puede clonar y explorar sin errores
- ✅ Documentación está completa y es legible
- ✅ `git status` está limpio

## Tiempo total estimado

**90 minutos** (8 tasks × 10-20 min cada una)

---

## Notas adicionales

- **No hay código ejecutable en este change** — solo estructura y documentación
- **Los placeholders están marcados con comentarios** — facilita identificarlos después
- **Git limpio** — cada commit es atómico y independiente (puede rebasarse)
- **Documentación exhaustiva** — el próximo que clone el repo sabe exactamente dónde va cada cosa
