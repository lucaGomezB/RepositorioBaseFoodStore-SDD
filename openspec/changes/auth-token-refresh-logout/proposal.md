## Why

Users need to maintain their session beyond the short access token lifetime (15 minutes). The refresh token mechanism allows users to obtain new access tokens without re-entering credentials. Additionally, users need the ability to explicitly end their session (logout) and invalidate tokens if they suspect unauthorized access.

## What Changes

- Refresh token endpoint with automatic rotation (old token invalidated, new token issued)
- Logout endpoint that revokes refresh token in database
- Access token refresh without requiring user interaction

## Capabilities

### New Capabilities

- `token-refresh`: Automatic token refresh with rotation for improved security
- `session-management`: User-initiated session termination with token invalidation

### Modified Capabilities

- None - extends existing auth-login-register

## Impact

- **API**: New endpoints /api/v1/auth/refresh and /api/v1/auth/logout
- **Database**: Refresh tokens stored in refresh_token table with active/revoked status
- **Frontend**: Must implement automatic token refresh on 401 responses