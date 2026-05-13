# Tasks: setup-backend-config

## 1. Dependencies and Environment

- [x] 1.1 Add FastAPI and uvicorn to backend/requirements.txt
- [x] 1.2 Add SQLAlchemy to backend/requirements.txt
- [x] 1.3 Add python-dotenv to backend/requirements.txt
- [x] 1.4 Add pydantic to backend/requirements.txt
- [x] 1.5 Install dependencies with pip install -r requirements.txt
- [x] 1.6 Verify DATABASE_URL in backend/.env (create if missing)

## 2. Core Configuration Module

- [x] 2.1 Update backend/app/core/config.py to load environment variables
- [x] 2.2 Add Settings class with pydantic BaseSettings
- [x] 2.3 Include: DATABASE_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
- [x] 2.4 Test config loading with `python -c "from app.core.config import settings; print(settings.DATABASE_URL)"`

## 3. Database Connection Module

- [x] 3.1 Update backend/app/core/database.py with SQLAlchemy engine creation
- [x] 3.2 Configure engine with DATABASE_URL from settings
- [x] 3.3 Create SessionLocal for session factory
- [x] 3.4 Implement get_db() dependency function
- [x] 3.5 Add session cleanup (close after request)
- [x] 3.6 Test: `python -c "from app.core.database import engine; print(engine)"` should work

## 4. Security Helpers Module

- [x] 4.1 Update backend/app/core/security.py with password hashing functions
- [x] 4.2 Implement hash_password() using bcrypt
- [x] 4.3 Implement verify_password() using bcrypt
- [x] 4.4 Add JWT configuration constants/structs
- [x] 4.5 Test: `python -c "from app.core.security import hash_password, verify_password; h=hash_password('test'); print(verify_password('test', h))"`

## 5. FastAPI Application Setup

- [x] 5.1 Update backend/app/main.py to create FastAPI app instance
- [x] 5.2 Add app title "Food Store API" and version "1.0.0"
- [x] 5.3 Configure CORS middleware for localhost:5173
- [x] 5.4 Create /health endpoint returning {"status": "ok"}
- [x] 5.5 Verify: `python -c "from app.main import app; print(app.title)"`

## 6. API Router Setup

- [x] 6.1 Create backend/app/api/__init__.py directory
- [x] 6.2 Create root router in backend/app/api/__init__.py
- [x] 6.3 Include health check route in router
- [x] 6.4 Mount router in app/main.py at /api/v1
- [x] 6.5 Verify: GET http://localhost:8000/api/v1/health returns 200

## 7. Verification and Documentation

- [x] 7.1 Run uvicorn and verify app starts: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [x] 7.2 Test health endpoint: `curl http://localhost:8000/health`
- [x] 7.3 Verify Swagger UI accessible: http://localhost:8000/docs
- [x] 7.4 Update backend/README.md with startup instructions
- [x] 7.5 Run: `git add . && git commit -m "feat: setup backend config (FastAPI, SQLAlchemy, security)"`

## Summary

All tasks should result in a working FastAPI backend that:
- Starts with `uvicorn app.main:app --reload`
- Has a health check at `/health`
- Has Swagger docs at `/docs`
- Can connect to PostgreSQL via SQLAlchemy
- Has password hashing utilities available