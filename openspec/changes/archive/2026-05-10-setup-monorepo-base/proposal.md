# Proposal: setup-monorepo-base

## ¿Qué se va a construir?

La estructura base del repositorio monorepo de Food Store con separación clara entre backend (FastAPI) y frontend (React + TypeScript). Sin esta estructura, ningún otro change puede empezar.

## ¿Por qué es necesario?

1. **Punto de partida obligatorio**: Todos los cambios siguientes dependen de esta estructura.
2. **Claridad arquitectónica**: Frontend y backend separados evitan mezclas accidentales.
3. **Convenciones consistentes**: .gitignore, README, .env.example documentados desde el inicio.
4. **Historial de Git limpio**: Commits progresivos, no un "big bang" monolítico.

## Historias de usuario cubiertas

- **US-000**: Scaffolding del monorepo y estructura base

## Funcionalidades incluidas

1. Estructura de carpetas para backend (`/backend`) y frontend (`/frontend`)
2. Archivo `.gitignore` que excluye artefactos de build, dependencias, archivos de entorno y DS_Store
3. `README.md` raíz con:
   - Descripción del proyecto
   - Instrucciones de setup para ambas capas
   - Links a documentación técnica
   - Requisitos previos (Node.js, Python 3.10+, PostgreSQL 15+)
4. `.env.example` en backend y frontend con todas las variables documentadas
5. Estructura modular del backend (`feature-first`):
   - `/backend/app/modules/` para módulos funcionales
   - `/backend/app/core/` para configuración compartida
   - `/backend/tests/` para tests
6. Estructura FSD (Feature-Sliced Design) del frontend:
   - `/frontend/src/app/`, `/frontend/src/pages/`, `/frontend/src/features/`, `/frontend/src/entities/`, `/frontend/src/shared/`
7. Commits progresivos documentando cada paso de la estructura

## Dependencias

Ninguna. Este es el punto de partida.

## Criterios de aceptación

- ✅ El repositorio Git está inicializado con mensajes de commit descriptivos
- ✅ Estructura `/backend` y `/frontend` claramente separadas y funcionales
- ✅ `.gitignore` correctamente configurado (excluye `.env`, `__pycache__/`, `node_modules/`, `.venv/`, `*.pyc`, `dist/`, `.DS_Store`)
- ✅ `README.md` raíz contiene: descripción, prerequisites, setup instructions, links a docs
- ✅ `.env.example` en ambas carpetas con variables documentadas y valores de ejemplo
- ✅ Estructura backend: `app/modules/`, `app/core/`, `tests/`, `requirements.txt` placeholder
- ✅ Estructura frontend: `src/app/`, `src/pages/`, `src/features/`, `src/entities/`, `src/shared/`, `package.json` placeholder
- ✅ Al menos 5 commits progresivos (estructura, gitignore, readme, env examples, directorios vacíos)
- ✅ Se puede clonar y explorar sin errores

## Reglas de negocio asociadas

- **RN-DA02**: Los IDs de seed (Roles, EstadoPedido) son estables. Se referencian explícitamente en el código. (Este change no los crea, pero prepara el lugar donde irán)

## Notas técnicas

- Git strategy: Rebase-friendly. Commits pequeños y descriptivos.
- Lenguaje: Conventional commits (feat:, docs:, chore:)
- Backend estructura: Feature-first (vertical slicing)
- Frontend estructura: Feature-Sliced Design (FSD) — capas horizontales + segmentos verticales
- Ambas estructuras respetan dependencias unidireccionales: nunca imports circulares
