## 1. Exception Classes

- [x] 1.1 Create `app/core/exceptions.py` with base `AppException` class
- [x] 1.2 Add `NotFoundException` (HTTP 404)
- [x] 1.3 Add `ValidationException` (HTTP 422)
- [x] 1.4 Add `UnauthorizedException` (HTTP 401)
- [x] 1.5 Add `ForbiddenException` (HTTP 403)
- [x] 1.6 Add `ServiceUnavailableException` (HTTP 503)

## 2. RFC 7807 Response Schema

- [x] 2.1 Create `app/core/schemas/error.py` with ProblemDetail schema
- [x] 2.2 Add field "type" (URI reference for error category)
- [x] 2.3 Add field "title" (human-readable error title)
- [x] 2.4 Add field "status" (HTTP status code)
- [x] 2.5 Add field "detail" (specific error message)
- [x] 2.6 Add field "errors" (optional array for validation errors)

## 3. Global Exception Handler

- [x] 3.1 Create `app/core/handlers.py` with exception handler functions
- [x] 3.2 Register handlers in `app/main.py`
- [x] 3.3 Handle HTTP exceptions (re-throw as problem details)
- [x] 3.4 Handle generic exceptions (return 500 with generic message)
- [x] 3.5 Add logging for unhandled exceptions

## 4. Request Validation Integration

- [x] 4.1 Verify Pydantic validation is working in existing endpoints
- [x] 4.2 Add response_model to endpoints to ensure consistent error format
- [x] 4.3 Test validation error responses follow RFC 7807

## 5. Input Sanitization

- [x] 5.1 Create `app/core/sanitization.py` with string sanitization functions
- [x] 5.2 Implement HTML/script tag removal
- [x] 5.3 Implement whitespace trimming utility
- [x] 5.4 Integrate sanitization into repository layer for string fields
- [x] 5.5 Add file upload validation utility (type and size limits)

## 6. Testing

- [x] 6.1 Add unit tests for custom exception classes
- [x] 6.2 Add unit tests for sanitization functions
- [x] 6.3 Verify error responses follow RFC 7807 format
- [x] 6.4 Test validation error scenarios

## 7. Integration with main.py

- [x] 7.1 Register all exception handlers in FastAPI app
- [x] 7.2 Test end-to-end error scenarios
- [x] 7.3 Verify build succeeds without errors