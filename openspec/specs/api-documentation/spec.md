## ADDED Requirements

### Requirement: API endpoints MUST have consistent OpenAPI tags
Every router SHALL define tags using ASCII-only names in English. Tags SHALL group endpoints by functional domain.

#### Scenario: All endpoints have ASCII tags
- **WHEN** inspecting the OpenAPI schema at /openapi.json
- **THEN** every endpoint SHALL have at least one tag using only ASCII characters

#### Scenario: Admin endpoints have sub-tags
- **WHEN** inspecting the OpenAPI schema
- **THEN** admin endpoints SHALL be grouped under specific tags (e.g., "Admin / Dashboard", "Admin / Users", "Admin / Orders", "Admin / Stock", "Admin / Config") instead of a generic tag

### Requirement: Endpoints MUST have explicit response_model
Every endpoint that returns data SHALL declare a `response_model` in its decorator.

#### Scenario: Response model declared
- **WHEN** inspecting each endpoint decorator
- **THEN** it SHALL have `response_model=<SomeSchema>` defined

#### Scenario: Swagger shows response schema
- **WHEN** visiting /docs
- **THEN** each endpoint SHALL display its response schema

### Requirement: Schemas MUST include examples
Pydantic schemas SHALL include `json_schema_extra={"example": ...}` on key fields to document expected values.

#### Scenario: Key schemas have examples
- **WHEN** inspecting the OpenAPI schema
- **THEN** request/response schemas SHALL include example values for key fields

### Requirement: Swagger UI and ReDoc MUST be accessible
The API SHALL serve interactive documentation at /docs (Swagger UI) and /redoc (ReDoc).

#### Scenario: Swagger UI loads
- **WHEN** visiting GET /docs
- **THEN** the Swagger UI page SHALL load and display all endpoints

#### Scenario: ReDoc loads
- **WHEN** visiting GET /redoc
- **THEN** the ReDoc page SHALL load and display all endpoints
