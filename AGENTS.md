# AGENTS.md — Food Store · Gestion de Pedidos

Este archivo es un **indice** que apunta al canonico del proyecto.

**Canonico**: `.opencode/AGENTS.md` (399 lineas)

> Toda la configuracion de agente, reglas, skills, protocolos y flujo OPSX
> estan definidos en `.opencode/AGENTS.md`. Por favor referirse a ese archivo.

## Resumen Ejecutivo

- **Stack**: FastAPI + SQLModel + PostgreSQL (backend) / React 18 + TypeScript + Vite + Tailwind (frontend)
- **Arquitectura Backend**: Router -> Service -> UoW -> Repository -> Model (unidireccional)
- **Arquitectura Frontend**: Feature-Sliced Design (Pages -> Features -> Entities -> Shared)
- **Auth**: JWT + RBAC (4 roles) + refresh token httpOnly cookie
- **Metodologia**: Spec-Driven Development (OPSX)
- **Cambios activos**: `openspec/` directorio, usar `openspec list --json`
