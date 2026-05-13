## ADDED Requirements

### Requirement: Create delivery address
The system SHALL allow an authenticated CLIENT user to create a new delivery address. The system SHALL auto-mark the first address as default.

#### Scenario: Create address successfully
- **WHEN** an authenticated CLIENT sends POST /api/v1/direcciones with valid fields
- **THEN** the system SHALL return HTTP 201 with the created address
- **AND** if this is the user's first address, es_predeterminada SHALL be true

#### Scenario: Create address without auth
- **WHEN** an unauthenticated user sends POST /api/v1/direcciones
- **THEN** the system SHALL return HTTP 401 Unauthorized

### Requirement: List user addresses
The system SHALL return all addresses belonging to the authenticated user, indicating which is the default.

#### Scenario: List own addresses
- **WHEN** an authenticated CLIENT sends GET /api/v1/direcciones
- **THEN** the system SHALL return HTTP 200 with only that user's addresses
- **AND** the response SHALL indicate which address is predeterminada

### Requirement: Update delivery address
The system SHALL allow updating an address, validating ownership.

#### Scenario: Update own address
- **WHEN** an authenticated user sends PUT /api/v1/direcciones/{id} with valid fields
- **THEN** the system SHALL return HTTP 200 with the updated address

#### Scenario: Update another user's address
- **WHEN** an authenticated user sends PUT /api/v1/direcciones/{id} for an address owned by another user
- **THEN** the system SHALL return HTTP 404 Not Found

### Requirement: Delete delivery address
The system SHALL allow deleting an address, validating ownership.

#### Scenario: Delete own address
- **WHEN** an authenticated user sends DELETE /api/v1/direcciones/{id}
- **THEN** the system SHALL return HTTP 204 No Content

#### Scenario: Delete nonexistent address
- **WHEN** an authenticated user sends DELETE /api/v1/direcciones/99999
- **THEN** the system SHALL return HTTP 404 Not Found

### Requirement: Set default address
The system SHALL allow setting an address as default, atomically removing the default flag from the previous one.

#### Scenario: Set address as default
- **WHEN** an authenticated user sends PATCH /api/v1/direcciones/{id}/predeterminada
- **THEN** the system SHALL set that address as es_predeterminada=true
- **AND** all other addresses for that user SHALL have es_predeterminada=false
