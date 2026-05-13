## ADDED Requirements

### Requirement: Route Protection
The system SHALL protect frontend routes based on authentication status and user role.

#### Scenario: Unauthenticated user is redirected to login
- **WHEN** an unauthenticated user navigates to a protected route
- **THEN** the system SHALL redirect to /login

#### Scenario: Authenticated user accesses protected route
- **WHEN** an authenticated user with sufficient role navigates to a protected route
- **THEN** the system SHALL render the route content

#### Scenario: User without required role sees 403
- **WHEN** an authenticated user without the required role navigates to a restricted route
- **THEN** the system SHALL display a 403 "Access Denied" message

#### Scenario: Public routes accessible without authentication
- **WHEN** an unauthenticated user navigates to a public route
- **THEN** the system SHALL render the route content normally

### Requirement: Automatic JWT Attachment
The HTTP client SHALL automatically attach the JWT access token to every authenticated request.

#### Scenario: Token attached to request
- **WHEN** an authenticated user makes an API request
- **THEN** the system SHALL include `Authorization: Bearer <token>` header automatically

### Requirement: Automatic Token Refresh on 401
The system SHALL automatically refresh the access token when receiving a 401 response, and retry the original request.

#### Scenario: Single request triggers refresh
- **WHEN** a request returns 401 Unauthorized
- **THEN** the system SHALL call POST /api/v1/auth/refresh with the stored refreshToken
- **AND** on success, update the authStore with new tokens
- **AND** retry the original request with the new access token

#### Scenario: Concurrent requests share refresh (request queue)
- **WHEN** multiple requests fail with 401 simultaneously
- **THEN** only ONE refresh request SHALL be made
- **AND** all pending requests SHALL be retried with the new token upon refresh completion

#### Scenario: Refresh token also expired
- **WHEN** the refresh token itself has expired
- **THEN** the system SHALL redirect to /login
