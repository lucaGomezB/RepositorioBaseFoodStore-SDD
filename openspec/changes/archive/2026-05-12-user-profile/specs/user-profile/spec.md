## ADDED Requirements

### Requirement: View own profile
The system SHALL allow an authenticated user to view their own profile data.

#### Scenario: View profile
- **WHEN** an authenticated user sends GET /api/v1/perfil
- **THEN** the system SHALL return HTTP 200 with nombre, email, telefono, fecha_creacion

#### Scenario: View profile without auth
- **WHEN** an unauthenticated user sends GET /api/v1/perfil
- **THEN** the system SHALL return HTTP 401 Unauthorized

### Requirement: Update own profile
The system SHALL allow an authenticated user to update their nombre and telefono. Email SHALL NOT be changeable.

#### Scenario: Update profile successfully
- **WHEN** an authenticated user sends PUT /api/v1/perfil with valid nombre and telefono
- **THEN** the system SHALL return HTTP 200 with the updated profile

#### Scenario: Email cannot be changed
- **WHEN** an authenticated user sends PUT /api/v1/perfil with a different email
- **THEN** the system SHALL ignore the email field and keep the original

### Requirement: Change password
The system SHALL allow an authenticated user to change their password by providing the current password and a new one.

#### Scenario: Change password successfully
- **WHEN** an authenticated user sends PUT /api/v1/perfil/password with correct password_actual and valid password_nueva
- **THEN** the system SHALL hash and persist the new password
- **AND** revoke all existing refresh tokens for that user
- **AND** return HTTP 200

#### Scenario: Wrong current password
- **WHEN** an authenticated user sends PUT /api/v1/perfil/password with incorrect password_actual
- **THEN** the system SHALL return HTTP 400 with detail "Contraseña actual incorrecta"

#### Scenario: Weak new password
- **WHEN** an authenticated user sends PUT /api/v1/perfil/password with password_nueva shorter than 8 characters
- **THEN** the system SHALL return HTTP 422 with validation error
