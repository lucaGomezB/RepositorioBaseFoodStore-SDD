## ADDED Requirements

### Requirement: RFC 7807 Problem Details Format
All API error responses SHALL follow RFC 7807 Problem Details format.

#### Scenario: Validation error response
- **WHEN** a request fails Pydantic validation
- **THEN** the response SHALL have Content-Type: application/problem+json with body containing "type", "title", "status", "detail", and "errors" fields

#### Scenario: Not found error response
- **WHEN** a resource is not found (e.g., GET /productos/999)
- **THEN** the response SHALL return status 404 with problem details including "type": "https://api.foodstore.com/errors/not-found"

#### Scenario: Unauthorized error response
- **WHEN** a request is made without valid authentication
- **THEN** the response SHALL return status 401 with problem details including "type": "https://api.foodstore.com/errors/unauthorized"

#### Scenario: Forbidden error response
- **WHEN** a user lacks permission for the requested operation
- **THEN** the response SHALL return status 403 with problem details including "type": "https://api.foodstore.com/errors/forbidden"

### Requirement: Custom Exception Hierarchy
The system SHALL provide custom exception classes for different error scenarios.

#### Scenario: Creating NotFoundException
- **WHEN** a requested resource does not exist
- **THEN** raising NotFoundException SHALL result in HTTP 404 response

#### Scenario: Creating ValidationException
- **WHEN** business logic validation fails
- **THEN** raising ValidationException SHALL result in HTTP 422 response with detailed error information

#### Scenario: Creating UnauthorizedException
- **WHEN** authentication fails
- **THEN** raising UnauthorizedException SHALL result in HTTP 401 response

#### Scenario: Creating ForbiddenException
- **WHEN** user lacks required role/permission
- **THEN** raising ForbiddenException SHALL result in HTTP 403 response

### Requirement: Global Exception Handler
The system SHALL register a global exception handler that catches all unhandled exceptions.

#### Scenario: Unhandled exception in endpoint
- **WHEN** an endpoint raises an unhandled exception
- **THEN** the handler SHALL convert it to a problem details response with status 500
- **AND** the handler SHALL log the error details for debugging

#### Scenario: Database connection failure
- **WHEN** the database connection fails
- **THEN** the handler SHALL return a problem details response with status 503 and "type": "https://api.foodstore.com/errors/service-unavailable"