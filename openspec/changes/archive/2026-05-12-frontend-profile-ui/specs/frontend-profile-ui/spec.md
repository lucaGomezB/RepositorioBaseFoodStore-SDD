## ADDED Requirements

### Requirement: View profile information
The system SHALL display the user's profile information: nombre, email, teléfono, and fecha de registro.

#### Scenario: Profile page loads user data
- **WHEN** an authenticated user navigates to /perfil
- **THEN** the system SHALL display nombre, email, telefono, and fecha_creacion
- **AND** show a loading skeleton while fetching

### Requirement: Edit profile
The system SHALL allow editing nombre and telefono through a form.

#### Scenario: Save profile changes
- **WHEN** a user edits nombre and telefono and clicks save
- **THEN** the system SHALL call PUT /perfil with the new data
- **AND** show a success toast
- **AND** update the auth store

### Requirement: Change password
The system SHALL provide a form to change password with current and new password fields.

#### Scenario: Change password successfully
- **WHEN** a user fills current and new password and submits
- **THEN** the system SHALL call PUT /perfil/password
- **AND** show a success toast

#### Scenario: Wrong current password
- **WHEN** a user submits wrong current password
- **THEN** the system SHALL show an error toast with the backend message

### Requirement: Manage addresses
The system SHALL allow listing, creating, editing, deleting, and setting default delivery addresses.

#### Scenario: List addresses
- **WHEN** a user views their profile
- **THEN** the system SHALL display their delivery addresses
- **AND** indicate which one is default

#### Scenario: Create address
- **WHEN** a user fills the address form and submits
- **THEN** the system SHALL create the address via POST /direcciones
- **AND** refresh the address list

#### Scenario: Set default address
- **WHEN** a user clicks "Set as default" on an address
- **THEN** the system SHALL call PATCH /direcciones/{id}/predeterminada
- **AND** update the displayed default indicator

#### Scenario: Delete address
- **WHEN** a user clicks delete on an address
- **THEN** the system SHALL confirm and call DELETE /direcciones/{id}
- **AND** remove it from the list
