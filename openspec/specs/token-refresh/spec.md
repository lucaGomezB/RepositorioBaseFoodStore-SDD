# token-refresh Specification

## Purpose
TBD - created by archiving change auth-token-refresh-logout. Update Purpose after archive.
## Requirements
### Requirement: Token Refresh with Rotation
The system SHALL provide a refresh token endpoint that issues new access tokens while rotating the refresh token.

#### Scenario: Valid refresh token request
- **WHEN** a user sends a valid refresh token to POST /api/v1/auth/refresh
- **THEN** the system SHALL return a new access_token and refresh_token
- **AND** the old refresh token SHALL be marked as revoked in the database

#### Scenario: Expired refresh token
- **WHEN** a user sends an expired refresh token to POST /api/v1/auth/refresh
- **THEN** the system SHALL return HTTP 401 with detail "Invalid or expired token"

#### Scenario: Revoked refresh token
- **WHEN** a user sends a revoked refresh token to POST /api/v1/auth/refresh
- **THEN** the system SHALL return HTTP 401 with detail "Refresh token not found or revoked"

#### Scenario: Invalid refresh token format
- **WHEN** a user sends a token that is not a refresh token type
- **THEN** the system SHALL return HTTP 401 with detail "Invalid token type"

### Requirement: Logout with Token Revocation
The system SHALL provide a logout endpoint that revokes the refresh token.

#### Scenario: Successful logout
- **WHEN** an authenticated user calls POST /api/v1/auth/logout with a valid refresh token
- **THEN** the refresh token SHALL be marked as revoked in the database
- **AND** the system SHALL return "Logged out successfully"

#### Scenario: Logout with already revoked token
- **WHEN** a user attempts to logout with an already revoked token
- **THEN** the system SHALL still return success (idempotent operation)

### Requirement: Multiple Device Support
The system SHALL allow multiple valid refresh tokens (one per device).

#### Scenario: User logs in from multiple devices
- **WHEN** a user logs in from device A and later from device B
- **THEN** both devices SHALL have independent valid refresh tokens
- **AND** revoking token on device A SHALL NOT affect session on device B

