# Spec: backend-app-configuration

## Overview

This spec defines the FastAPI application setup including the main app instance, CORS configuration, middleware, and health check endpoint.

## ADDED Requirements

### Requirement: FastAPI app instance created

The system SHALL create a FastAPI application instance in `app/main.py` with basic configuration.

#### Scenario: App can be imported
- **GIVEN** the backend code is installed
- **WHEN** running `python -c "from app.main import app"`
- **THEN** no ImportError is raised
- **AND** `app` is a valid FastAPI instance

#### Scenario: App has title and version
- **GIVEN** the FastAPI app instance
- **WHEN** accessing `/openapi.json`
- **THEN** the JSON contains `info.title` set to "Food Store API"
- **AND** `info.version` is set to "1.0.0"

---

### Requirement: CORS middleware configured

The system SHALL configure CORS to allow frontend development server access.

#### Scenario: CORS allows localhost:5173
- **GIVEN** the FastAPI app is running
- **WHEN** a request is made from http://localhost:5173 with Origin header
- **THEN** the response includes Access-Control-Allow-Origin header

#### Scenario: CORS is configurable via environment
- **GIVEN** CORS_ORIGINS is set in environment
- **WHEN** the app starts
- **THEN** only the configured origins are allowed

---

### Requirement: Health check endpoint available

The system SHALL provide a `/health` endpoint that returns a successful status.

#### Scenario: Health endpoint returns 200
- **GIVEN** the FastAPI app is running
- **WHEN** GET request is made to `/health`
- **THEN** response status code is 200
- **AND** response body contains `{"status": "ok"}`

---

### Requirement: App runs with uvicorn

The system SHALL allow the app to be started with uvicorn.

#### Scenario: Uvicorn starts successfully
- **GIVEN** the backend code is installed
- **WHEN** running `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **THEN** the server starts without errors
- **AND** it listens on port 8000

#### Scenario: Hot reload works
- **GIVEN** uvicorn is running with `--reload`
- **WHEN** a Python file in app/ is modified
- **THEN** the server reloads automatically