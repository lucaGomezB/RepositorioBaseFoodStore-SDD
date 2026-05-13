## ADDED Requirements

### Requirement: General Role-Based Access Control (RBAC)
The system SHALL provide a reusable authorization dependency that verifies the current user has one of the required roles before allowing access to an endpoint.

#### Scenario: Access allowed with sufficient role
- **WHEN** an authenticated user with role ADMIN accesses an endpoint requiring ADMIN
- **THEN** the system SHALL allow the request and return the expected response

#### Scenario: Access denied with insufficient role
- **WHEN** an authenticated user with role CLIENT accesses an endpoint requiring ADMIN
- **THEN** the system SHALL return HTTP 403 Forbidden with detail "Insufficient permissions"

#### Scenario: Access denied without authentication
- **WHEN** an unauthenticated request accesses a protected endpoint
- **THEN** the system SHALL return HTTP 401 Unauthorized

### Requirement: Role Enum Definition
The system SHALL define an `IntEnum` with the 4 stable role IDs matching seed data: ADMIN(1), STOCK(2), PEDIDOS(3), CLIENT(4).

#### Scenario: Role enum values match seed
- **WHEN** the Role enum is accessed
- **THEN** ADMIN SHALL equal 1, STOCK SHALL equal 2, PEDIDOS SHALL equal 3, CLIENT SHALL equal 4

### Requirement: Admin Role Assignment Endpoint
The system SHALL provide an endpoint `PUT /api/auth/users/{user_id}/role` that allows ADMIN users to change the role of another user.

#### Scenario: Admin assigns role to user
- **WHEN** an authenticated ADMIN sends PUT /api/auth/users/{id}/role with a valid role_id
- **THEN** the user's role SHALL be updated
- **AND** the system SHALL return the updated user

#### Scenario: Non-admin cannot assign roles
- **WHEN** a non-ADMIN user sends PUT /api/auth/users/{id}/role
- **THEN** the system SHALL return HTTP 403

#### Scenario: Admin prevents self-degradation as last admin
- **WHEN** the last ADMIN in the system attempts to change their own role away from ADMIN
- **THEN** the system SHALL return HTTP 400 with detail "Cannot remove admin role from the last administrator"

### Requirement: Token Payload Role Reflects Database
When a user's role changes, the new role SHALL be reflected in new JWT tokens issued after the change.

#### Scenario: New tokens reflect updated role
- **WHEN** an ADMIN changes user's role from CLIENT to STOCK
- **AND** the user obtains a new access token (via login or refresh)
- **THEN** the new token SHALL contain the updated rol_id = 2 (STOCK)

### Requirement: Public Routes Do Not Require Auth
The system SHALL allow unauthenticated access to public routes: health check, login, register.

#### Scenario: Health endpoint accessible without auth
- **WHEN** an unauthenticated request hits GET /api/v1/health
- **THEN** the system SHALL return 200 OK

#### Scenario: Login endpoint accessible without auth
- **WHEN** an unauthenticated request hits POST /api/v1/auth/login
- **THEN** the system SHALL process the login normally
