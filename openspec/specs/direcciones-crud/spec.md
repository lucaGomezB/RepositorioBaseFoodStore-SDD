## ADDED Requirements

### Requirement: User can list their delivery addresses
The system SHALL display all delivery addresses belonging to the authenticated user, clearly indicating which one is the default.

#### Scenario: List own addresses
- **WHEN** a CLIENT or ADMIN user navigates to `/direcciones`
- **THEN** the system displays a table/list with all their addresses showing: calle, numero, ciudad, codigo postal, piso/depto (if set), and whether it is the default address

#### Scenario: Empty address list
- **WHEN** a user has no addresses saved
- **THEN** the system displays an empty state message "No tenés direcciones guardadas" and a button to add one

#### Scenario: Error loading addresses
- **WHEN** the API request fails
- **THEN** the system displays an error message with the error detail

### Requirement: User can create a new address
The system SHALL allow the authenticated user to add a new delivery address with calle, numero, ciudad, codigo postal, optional piso/depto, and optional latitud/longitud.

#### Scenario: Create address successfully
- **WHEN** the user fills in the form with calle, numero, ciudad, codigo_postal, and optional piso_depto, latitud, longitud and submits
- **THEN** the new address is saved and appears in the list
- **AND** if it is the user's first address, it is automatically marked as default (RN-DI01)

#### Scenario: Create address with missing required fields
- **WHEN** the user submits the form without required fields (calle, numero, ciudad, codigo_postal)
- **THEN** the system shows validation errors and does not submit

#### Scenario: Create address without coordinates
- **WHEN** the user does not provide latitud or longitud
- **THEN** the address is saved with latitud=null and longitud=null

#### Scenario: Provide out-of-range latitude
- **WHEN** the user submits latitud = 100 (outside -90 to 90)
- **THEN** the backend SHALL return validation error

#### Scenario: Provide out-of-range longitude
- **WHEN** the user submits longitud = 200 (outside -180 to 180)
- **THEN** the backend SHALL return validation error

### Requirement: User can edit an existing address
The system SHALL allow the user to update any of their own addresses, including clearing optional fields (piso_depto, latitud, longitud) by explicitly setting them to null.

#### Scenario: Edit address successfully
- **WHEN** the user modifies an address and submits
- **THEN** the changes are saved and the list updates

#### Scenario: Edit address owned by another user
- **WHEN** a user tries to edit an address they do not own
- **THEN** the backend returns 404 (ownership validation) and the frontend shows an error

#### Scenario: Clear optional fields on edit
- **WHEN** the user clears piso_depto, latitud, and longitud fields in the form and submits
- **THEN** those fields are saved as null in the database

#### Scenario: Edit address to clear coordinates
- **WHEN** the user edits an address that has coordinates and clears both latitud and longitud fields
- **THEN** the address is saved with latitud=null and longitud=null

### Requirement: User can delete an address
The system SHALL allow the user to delete their own addresses with confirmation.

#### Scenario: Delete address successfully
- **WHEN** the user clicks "Eliminar" and confirms
- **THEN** the address is removed from the list (backend returns 204)

#### Scenario: Delete is cancelled
- **WHEN** the user clicks "Eliminar" and then cancels the confirmation
- **THEN** the address is not deleted and the list remains unchanged

### Requirement: User can set a default address
The system SHALL allow the user to mark any of their addresses as the default delivery address.

#### Scenario: Set default address
- **WHEN** the user clicks "Establecer como predeterminada" on a non-default address
- **THEN** that address becomes the default and the previous default loses that status (RN-DI02)

#### Scenario: Address is already default
- **WHEN** the default address is displayed
- **THEN** it shows a "Predeterminada" badge and does NOT show the "Establecer como predeterminada" button

### Requirement: User can select current location via Geolocation API
The system SHALL provide a "Usar ubicacion actual" button in the address form that captures the device's current position using the browser Geolocation API.

#### Scenario: Location permission granted
- **WHEN** the user clicks "Usar ubicacion actual"
- **AND** the browser grants geolocation permission
- **THEN** the latitud and longitud inputs are auto-filled with the device's current coordinates
- **AND** a success indicator is shown

#### Scenario: Location permission denied
- **WHEN** the user clicks "Usar ubicacion actual"
- **AND** the browser denies geolocation permission
- **THEN** an inline error message "No se pudo obtener la ubicacion. Ingresa las coordenadas manualmente." is shown
- **AND** the user can still enter coordinates manually

#### Scenario: Geolocation unavailable
- **WHEN** the user clicks "Usar ubicacion actual"
- **AND** the device does not support geolocation
- **THEN** an inline error message is shown
- **AND** the button is disabled for the remainder of the session
