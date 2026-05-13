# Spec: monorepo-structure

## Overview

This spec defines the foundational structure of the Food Store monorepo. It establishes the physical organization of code, configuration, and documentation required for subsequent changes to be implemented. This is a prerequisite for all other capabilities.

## ADDED Requirements

### Requirement: Git repository initialized with conventional commits

The repository SHALL be initialized as a Git repository with a series of small, atomic commits following the Conventional Commits specification.

#### Scenario: Repository initialization
- **GIVEN** a fresh directory with no version control
- **WHEN** `git init` is executed in the root directory
- **THEN** a `.git` directory is created and the repository is ready for commits

#### Scenario: Progressive commits exist
- **GIVEN** a Git repository initialized
- **WHEN** `git log --oneline` is executed
- **THEN** at least 5 commits exist with descriptive messages following `type: description` format
- **AND** commit messages use types: `chore:`, `docs:`, or `feat:`

#### Scenario: Commit messages are descriptive
- **GIVEN** a Git repository with commits
- **WHEN** examining commit messages via `git log`
- **THEN** each message clearly describes what was changed (e.g., "chore: scaffold backend directory structure")

---

### Requirement: Monorepo directory structure established

The repository SHALL contain two distinct top-level directories: `backend/` for the server application and `frontend/` for the client application.

#### Scenario: Root directory contains backend and frontend
- **GIVEN** a fresh clone of the repository
- **WHEN** listing root directory contents with `ls -la`
- **THEN** both `backend/` and `frontend/` directories exist
- **AND** each directory contains a meaningful structure

#### Scenario: Backend directory is functional
- **GIVEN** the `backend/` directory exists
- **WHEN** exploring the directory structure
- **THEN** it contains `app/`, `tests/`, `requirements.txt`, `.env.example`, and `README.md`

#### Scenario: Frontend directory is functional
- **GIVEN** the `frontend/` directory exists
- **WHEN** exploring the directory structure
- **THEN** it contains `src/`, `public/`, `package.json`, `.env.example`, and `README.md`

---

### Requirement: .gitignore excludes build artifacts and sensitive files

The repository SHALL have a `.gitignore` file in its root that excludes development artifacts, dependencies, environment files, and operating system files.

#### Scenario: .gitignore exists in root
- **GIVEN** the repository root
- **WHEN** checking for `.gitignore`
- **THEN** the file exists and contains appropriate exclusion rules

#### Scenario: Python artifacts are ignored
- **GIVEN** `.gitignore` is configured
- **WHEN** Python files are created in `backend/`
- **THEN** `.env`, `__pycache__/`, `*.pyc`, `.venv/`, `dist/`, `build/` are ignored

#### Scenario: Node.js artifacts are ignored
- **GIVEN** `.gitignore` is configured
- **WHEN** Node.js files are created in `frontend/`
- **THEN** `node_modules/`, `.env.local`, `dist/`, `.DS_Store` are ignored

#### Scenario: IDE and OS files are ignored
- **GIVEN** `.gitignore` is configured
- **WHEN** IDE or OS files are created
- **THEN** `.vscode/`, `.idea/`, `*.swp`, `.DS_Store` are ignored

---

### Requirement: Root README contains complete project documentation

The root `README.md` SHALL contain project description, prerequisites, setup instructions for both backend and frontend, links to documentation, and technology stack information.

#### Scenario: README exists in root
- **GIVEN** the repository root
- **WHEN** checking for `README.md`
- **THEN** the file exists and is readable

#### Scenario: README contains project description
- **GIVEN** `README.md` exists
- **WHEN** reading the file content
- **THEN** it contains a clear description of the Food Store project

#### Scenario: README lists prerequisites
- **GIVEN** `README.md` exists
- **WHEN** reading the prerequisites section
- **THEN** it specifies: Node.js 18+, Python 3.10+, PostgreSQL 15+, Git 2.x

#### Scenario: README contains backend setup instructions
- **GIVEN** `README.md` exists
- **WHEN** reading the setup section
- **THEN** it contains step-by-step instructions for backend setup including: virtual environment creation, dependency installation, environment file setup, and server startup commands

#### Scenario: README contains frontend setup instructions
- **GIVEN** `README.md` exists
- **WHEN** reading the setup section
- **THEN** it contains step-by-step instructions for frontend setup including: npm install, environment file setup, and dev server startup

#### Scenario: README contains access URLs
- **GIVEN** `README.md` exists
- **WHEN** reading the documentation
- **THEN** it specifies: Backend at http://localhost:8000, Frontend at http://localhost:5173

#### Scenario: README contains technology stack
- **GIVEN** `README.md` exists
- **WHEN** reading the stack section
- **THEN** it documents: FastAPI, SQLModel, PostgreSQL, React 18, TypeScript, Vite, Tailwind CSS

---

### Requirement: Environment variable templates exist in both layers

Both backend and frontend SHALL have `.env.example` files documenting all required environment variables with example values.

#### Scenario: Backend .env.example exists
- **GIVEN** the backend directory
- **WHEN** checking for `.env.example`
- **THEN** the file exists in `backend/`

#### Scenario: Backend .env.example is documented
- **GIVEN** `backend/.env.example` exists
- **WHEN** reading the file
- **THEN** it documents: DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, CORS_ORIGINS, MERCADOPAGO_ACCESS_TOKEN, MERCADOPAGO_PUBLIC_KEY, LOG_LEVEL, ENVIRONMENT

#### Scenario: Frontend .env.example exists
- **GIVEN** the frontend directory
- **WHEN** checking for `.env.example`
- **THEN** the file exists in `frontend/`

#### Scenario: Frontend .env.example is documented
- **GIVEN** `frontend/.env.example` exists
- **WHEN** reading the file
- **THEN** it documents: VITE_API_BASE_URL, VITE_MERCADOPAGO_PUBLIC_KEY, VITE_ENV

---

### Requirement: Backend uses feature-first directory structure

The backend SHALL use a feature-first (vertical slicing) directory structure with clear separation between core configuration and functional modules.

#### Scenario: Backend has app directory
- **GIVEN** the backend directory
- **WHEN** exploring `backend/app/`
- **THEN** it contains `main.py` and subdirectories

#### Scenario: Backend has core configuration
- **GIVEN** `backend/app/core/` exists
- **WHEN** exploring the directory
- **THEN** it contains: `config.py`, `database.py`, `security.py` (as placeholders or implementations)

#### Scenario: Backend has modules directory
- **GIVEN** `backend/app/modules/` exists
- **WHEN** exploring the directory
- **THEN** it contains subdirectories for: auth, usuarios, categorias, productos, pedidos, pagos, direcciones, admin, refreshtokens

#### Scenario: Backend has tests directory
- **GIVEN** the backend directory
- **WHEN** checking for test structure
- **THEN** `backend/tests/` exists with `conftest.py`

#### Scenario: Backend has requirements.txt
- **GIVEN** the backend directory
- **WHEN** checking for dependencies
- **THEN** `backend/requirements.txt` exists

---

### Requirement: Frontend uses Feature-Sliced Design structure

The frontend SHALL use Feature-Sliced Design (FSD) with horizontal layers (app, pages, features, entities, shared) and vertical segments for each feature.

#### Scenario: Frontend has app layer
- **GIVEN** the frontend directory
- **WHEN** exploring `frontend/src/app/`
- **THEN** it contains: `App.tsx`, `router.tsx`, and optionally `app.css`

#### Scenario: Frontend has pages layer
- **GIVEN** the frontend directory
- **WHEN** exploring `frontend/src/pages/`
- **THEN** the directory exists with placeholder pages (HomePage, LoginPage, etc.)

#### Scenario: Frontend has features layer
- **GIVEN** the frontend directory
- **WHEN** exploring `frontend/src/features/`
- **THEN** it contains subdirectories for: auth, catalog, cart, orders, payments, admin

#### Scenario: Frontend has entities layer
- **GIVEN** the frontend directory
- **WHEN** exploring `frontend/src/entities/`
- **THEN** it contains subdirectories for: user, product, order, address

#### Scenario: Frontend has shared layer
- **GIVEN** the frontend directory
- **WHEN** exploring `frontend/src/shared/`
- **THEN** it contains subdirectories for: api, stores, components, hooks, types, utils, styles

#### Scenario: Frontend has package.json
- **GIVEN** the frontend directory
- **WHEN** checking for dependencies
- **THEN** `frontend/package.json` exists

---

### Requirement: Repository can be cloned and explored without errors

The repository SHALL be in a state where it can be cloned fresh and explored without causing errors or warnings.

#### Scenario: Clone succeeds without errors
- **GIVEN** a remote repository with this content
- **WHEN** executing `git clone <url>`
- **THEN** the clone completes without errors

#### Scenario: Directory listing succeeds
- **GIVEN** a cloned repository
- **WHEN** executing `ls -R` commands on backend and frontend
- **THEN** all directories are listable without errors

#### Scenario: No untracked files in clean state
- **GIVEN** a cloned repository
- **WHEN** executing `git status`
- **THEN** the working directory is clean (or contains only expected ignored files)

#### Scenario: README files are readable
- **GIVEN** a cloned repository
- **WHEN** reading README.md files (root, backend, frontend)
- **THEN** all files are readable and contain valid markdown

---

### Requirement: Each directory contains Python package markers

All Python directories SHALL contain `__init__.py` files to be recognized as proper packages by Python.

#### Scenario: All backend directories have __init__.py
- **GIVEN** the backend directory structure
- **WHEN** searching for Python packages
- **THEN** every directory under `backend/app/` contains `__init__.py`

#### Scenario: Tests directory has __init__.py
- **GIVEN** the `backend/tests/` directory
- **WHEN** checking for package marker
- **THEN** `backend/tests/__init__.py` exists