## Why

Currently the Food Store API lacks a centralized error handling mechanism. Each endpoint returns errors in different formats, making it difficult for frontend clients to handle errors consistently. Additionally, there is no input validation layer, allowing malformed or malicious data to reach the business logic layer.

## What Changes

- Create a centralized exception handler that converts all unhandled exceptions to RFC 7807 Problem Details format
- Implement custom exception classes for different error scenarios (validation, not found, unauthorized, etc.)
- Add request validation middleware using Pydantic models
- Create error response schemas that follow RFC 7807 standard
- Add input sanitization for string inputs to prevent injection attacks

## Capabilities

### New Capabilities

- `error-handling`: Centralized error handling with RFC 7807 Problem Details responses
- `input-validation`: Request validation using Pydantic models with clear error messages
- `input-sanitization`: String input sanitization to prevent XSS and injection attacks

### Modified Capabilities

- None

## Impact

- **Backend**: New modules in `app/core/exceptions.py` and `app/core/middleware/`
- **API**: All endpoints will return consistent error format
- **Dependencies**: Already using Pydantic (setup-backend-config), no new deps needed
- **Configuration**: Settings for error handling behavior (e.g., include debug info in dev)