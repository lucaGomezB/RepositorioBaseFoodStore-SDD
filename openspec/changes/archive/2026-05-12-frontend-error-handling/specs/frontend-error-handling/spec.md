## ADDED Requirements

### Requirement: Error Boundary
The system SHALL display a fallback UI when a React component crashes during rendering.

#### Scenario: Component crash shows fallback
- **WHEN** a React component throws an error during rendering
- **THEN** the ErrorBoundary SHALL display a friendly error message
- **AND** SHALL provide a "Reintentar" button to recover

### Requirement: HTTP Error Toasts
The system SHALL display toast notifications for HTTP errors via the Axios response interceptor.

#### Scenario: 400 validation error
- **WHEN** a request returns HTTP 400
- **THEN** the system SHALL show a toast with the validation error details

#### Scenario: 403 forbidden
- **WHEN** a request returns HTTP 403
- **THEN** the system SHALL show a toast with "No tenés permisos para esta acción"

#### Scenario: 404 not found
- **WHEN** a request returns HTTP 404
- **THEN** the system SHALL show a toast with "Recurso no encontrado"

#### Scenario: 429 rate limited
- **WHEN** a request returns HTTP 429
- **THEN** the system SHALL show a toast with "Demasiadas solicitudes, esperá un momento"

#### Scenario: 500 server error
- **WHEN** a request returns HTTP 500
- **THEN** the system SHALL show a toast with "Error interno, intentá de nuevo más tarde"

### Requirement: ToastContainer UI
The system SHALL render a stack of toast notifications in the top-right corner.

#### Scenario: Toast appears and auto-dismisses
- **WHEN** a toast is added to the store
- **THEN** it SHALL appear in the top-right corner
- **AND** auto-dismiss after 5 seconds
