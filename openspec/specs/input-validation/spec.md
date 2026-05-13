## ADDED Requirements

### Requirement: Request Body Validation
All API endpoints that accept request bodies SHALL validate the data using Pydantic models.

#### Scenario: Valid login request
- **WHEN** a POST /auth/login request contains valid email and password
- **THEN** the request SHALL pass validation and reach the endpoint handler

#### Scenario: Invalid email format
- **WHEN** a POST /auth/login request contains an invalid email format
- **THEN** the response SHALL return status 422 with validation error details for the "email" field

#### Scenario: Missing required field
- **WHEN** a POST /auth/login request is missing the "password" field
- **THEN** the response SHALL return status 422 indicating the missing required field

#### Scenario: String too long
- **WHEN** a request contains a string field exceeding the maximum length
- **THEN** the response SHALL return status 422 with "string_too_long" error

### Requirement: Query Parameter Validation
All API endpoints with query parameters SHALL validate the parameter types and ranges.

#### Scenario: Invalid pagination parameter
- **WHEN** GET /productos has page=-1
- **THEN** the response SHALL return status 422 with validation error for "page" parameter

#### Scenario: Valid pagination parameters
- **WHEN** GET /productos has page=1 and page_size=20
- **THEN** the request SHALL pass validation and reach the endpoint handler

### Requirement: Path Parameter Validation
Path parameters SHALL be validated for type and format.

#### Scenario: Invalid ID format
- **WHEN** GET /productos/abc receives a non-numeric ID
- **THEN** the response SHALL return status 422 with validation error for "id" parameter

#### Scenario: Valid ID format
- **WHEN** GET /productos/123 receives a valid integer ID
- **THEN** the request SHALL pass validation and reach the endpoint handler